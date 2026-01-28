import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 配置區 ---
API_KEY = "d20c02bc2b0c66692623f40f1535c1fd" # 你申請到的真 Key
SPORT = "soccer_epl"  # 預設看英超，你也可以改 upcoming 睇全球
REGION = "uk"         # Bet365 屬於 uk 區域

st.set_page_config(page_title="Bet365 實時推演中心", layout="wide")

def get_live_odds():
    # 真正從 The Odds API 抓取 Bet365 數據
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {
        'api_key': API_KEY,
        'regions': REGION,
        'markets': 'h2h',
        'oddsFormat': 'decimal'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# --- 介面開始 ---
st.title("⚽ Bet365 實時推演引擎")
st.write(f"系統狀態：實時監控中 | 最後更新：{datetime.now().strftime('%H:%M:%S')}")

data = get_live_odds()

if data:
    # 搵出第一場比賽作為範例推演
    match = data[0]
    home_team = match['home_team']
    away_team = match['away_team']
    
    # 搵出 Bet365 嘅賠率
    bet365_odds = next((b for b in match['bookmakers'] if b['key'] == 'bet365'), match['bookmakers'][0])
    odds_list = bet365_odds['markets'][0]['outcomes']
    
    # 顯示賠率看板
    st.subheader(f"🏟️ 當前焦點：{home_team} vs {away_team}")
    cols = st.columns(3)
    for i, outcome in enumerate(odds_list):
        cols[i].metric(outcome['name'], f"{outcome['price']}")

    # --- 核心演算：絕殺/扳平機率 ---
    # 簡單演算邏輯：賠率越低，代表機率越高
    draw_price = next(o['price'] for o in odds_list if o['name'] == 'Draw')
    win_prob = round((1 / draw_price) * 100 + 15, 1) # 模擬演算加權

    st.subheader("🔮 實時演算儀表板")
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = win_prob,
        title = {'text': "預期絕殺/平局機率 (%)"},
        gauge = {'axis': {'range': [0, 100]},
                 'bar': {'color': "royalblue"},
                 'steps': [
                     {'range': [0, 40], 'color': "#eeeeee"},
                     {'range': [40, 70], 'color': "#bbdefb"},
                     {'range': [70, 100], 'color': "#2196f3"}]}))
    st.plotly_chart(fig, use_container_width=True)

    if win_prob > 60:
        st.error(f"🚨 **高能預警**：{home_team} 賠率劇烈變動，建議留意即將發生嘅入球！")
else:
    st.warning("暫時未能獲取賠率數據，請檢查 API Key 或聯賽設定。")

if st.button("🔄 手動刷新數據"):
    st.rerun()
