import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 核心配置 ---
API_KEY = "d20c02bc2b0c66692623f40f1535c1fd" 

st.set_page_config(page_title="足球全能指揮中心", layout="wide", page_icon="⚽")

# --- CSS 美化 ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 側邊欄 ---
st.sidebar.title("🎮 戰術操控台")
app_mode = st.sidebar.radio("切換功能", ["🌍 API 實時監控", "🧠 手動養成推演"])

# --- 模式 1：API 實時監控 ---
if app_mode == "🌍 API 實時監控":
    st.title("🏟️ 聯賽實時數據中心")
    
    league_dict = {
        "英超 (EPL)": "soccer_epl",
        "西甲 (La Liga)": "soccer_spain_la_liga",
        "意甲 (Serie A)": "soccer_italy_serie_a",
        "德甲 (Bundesliga)": "soccer_germany_bundesliga",
        "法甲 (Ligue 1)": "soccer_france_ligue_1"
    }
    selected_league = st.sidebar.selectbox("選擇監控聯賽", list(league_dict.keys()))
    
    @st.cache_data(ttl=60) # 每分鐘才真正請求一次 API，節省額度並加快速度
    def get_data(sport_key):
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
        params = {'api_key': API_KEY, 'regions': 'uk', 'markets': 'h2h'}
        res = requests.get(url, params=params)
        return res.json() if res.status_code == 200 else []

    data = get_data(league_dict[selected_league])

    if data:
        st.success(f"✅ 已成功連接 {selected_league} 數據流")
        for match in data:
            # 轉換時間
            start_time = datetime.strptime(match['commence_time'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8)
            
            with st.container():
                st.markdown(f"### {match['home_team']} vs {match['away_team']}")
                st.caption(f"📅 開賽時間：{start_time.strftime('%Y-%m-%d %H:%M')}")
                
                # 提取 Bet365
                b365 = next((b for b in match['bookmakers'] if b['key'] == 'bet365'), match['bookmakers'][0])
                odds = {o['name']: o['price'] for o in b365['markets'][0]['outcomes']}
                
                c1, c2, c3, c4 = st.columns([1,1,1,2])
                c1.metric("🏠 主勝", odds.get(match['home_team']))
                c2.metric("🤝 和局", odds.get('Draw'))
                c3.metric("🚀 客勝", odds.get(match['away_team']))
                
                # 計算隱含機率
                draw_prob = (1 / odds.get('Draw')) * 100
                c4.progress(draw_prob / 100, text=f"📊 市場預期平局率: {draw_prob:.1f}%")
                st.divider()
    else:
        st.error("❌ 無法獲取數據，請檢查 API 額度或稍後再試。")

# --- 模式 2：手動養成推演 ---
else:
    st.title("🧠 深度戰術養成推演")
    
    with st.container():
        col_a, col_b = st.columns(2)
        with col_a:
            h_name = st.text_input("🏠 主隊", "沙士菲")
            h_score = st.number_input("比分", 0, 10, 0, key="h_s")
            h_red = st.number_input("🔴 紅牌", 0, 5, 0, key="h_r")
            h_danger = st.slider("🔥 危險進攻", 0, 100, 30)
        with col_b:
            a_name = st.text_input("🚀 客隊", "塔勒瑞斯")
            a_score = st.number_input("比分 ", 0, 10, 1, key="a_s")
            a_red = st.number_input("🔴 紅牌 ", 0, 5, 0, key="a_r")
            a_poss = st.slider("⚽ 控球率 (%)", 0, 100, 50)

        h_odds = st.number_input("即時主勝賠率", 1.0, 50.0, 2.8)
        
        if st.button("🔥 執行 AI 戰術演算"):
            # 演算邏輯：基礎賠率機率 + 壓力加權 - 紅牌懲罰
            prob = (1/h_odds)*100 + (h_danger * 0.5) - (h_red * 20) + (a_red * 20) + (h_poss - 50)*0.3
            prob = max(min(prob, 98.0), 2.0)

            st.divider()
            res_c1, res_c2 = st.columns([2,1])
            with res_c1:
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = prob,
                    title = {'text': f"{h_name} 反超/扳平指數"},
                    gauge = {
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#1f77b4"},
                        'steps': [
                            {'range': [0, 40], 'color': "#f8d7da"},
                            {'range': [40, 75], 'color': "#fff3cd"},
                            {'range': [75, 100], 'color': "#d4edda"}]
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
            with res_c2:
                st.subheader("📝 AI 診斷")
                if h_red > a_red: st.error("⚠️ 人數劣勢：勝率大幅下降")
                if h_danger > 50: st.success("🔥 狂攻模式：進球預期極高")
                st.write(f"當前演算顯示 {h_name} 有 `{prob:.1f}%` 的機會改變戰局。")
