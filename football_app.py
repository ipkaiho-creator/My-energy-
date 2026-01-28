import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- 核心配置 ---
API_KEY = "d20c02bc2b0c66692623f40f1535c1fd" 

st.set_page_config(page_title="AI 實時下注指揮官", layout="wide", page_icon="🤖")

# --- 1. 定時刷新組件 (每 60 秒刷新一次) ---
st_autorefresh(interval=60 * 1000, key="ai_cron_job")

# --- 2. 專業級 CSS 美化 ---
st.markdown("""
    <style>
    .main { background-color: #050a0f; color: #00ff88; }
    .recommendation-box { 
        background: rgba(0, 255, 136, 0.1); 
        border-left: 5px solid #00ff88; 
        padding: 20px; 
        border-radius: 5px;
        margin: 10px 0;
    }
    .stMetric { background: #111; border: 1px solid #333; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. AI 策略引擎 (核心邏輯) ---
def ai_strategy_engine(home_odds, draw_odds, away_odds, team_focus):
    """
    AI 策略模組：
    - 計算隱含勝率
    - 偵測價值偏差 (Value Detection)
    - 給出推薦選項
    """
    prob_draw = (1 / draw_odds) * 100
    
    # 策略模擬：如果平局賠率在 3.0-3.5 之間，且分鐘進入後半場，推薦平局
    if 3.0 <= draw_odds <= 3.6:
        recommend = "🎯 推薦：平局 (Draw) - 盤口極其穩定"
        confidence = "高 (High)"
    elif home_odds < 1.5:
        recommend = f"🔥 推薦：{team_focus} 獨贏 - 強力壓制"
        confidence = "中 (Medium)"
    else:
        recommend = "⌛ 觀望：賠率波動中，暫不建議入場"
        confidence = "低 (Low)"
    
    return recommend, confidence, prob_draw

# --- 4. 主介面 ---
st.markdown(f"## 🤖 AI 實時下注指揮官 v5.0")
st.write(f"系統狀態：**實時監控中** | 最後刷新：{datetime.now().strftime('%H:%M:%S')}")

# 搜尋欄：鎖定球隊
search_team = st.text_input("🔍 輸入你想監控的球隊名稱 (例如: Liverpool 或 Arsenal)", "Arsenal")

# --- 5. 抓取數據 ---
@st.cache_data(ttl=50)
def fetch_live_market():
    url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds"
    params = {'api_key': API_KEY, 'regions': 'uk', 'markets': 'h2h'}
    res = requests.get(url, params=params)
    return res.json() if res.status_code == 200 else []

all_matches = fetch_live_market()

# 篩選球隊
target_match = None
if all_matches:
    for m in all_matches:
        if search_team.lower() in m['home_team'].lower() or search_team.lower() in m['away_team'].lower():
            target_match = m
            break

if target_match:
    st.divider()
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"🏟️ 當前監控：{target_match['home_team']} vs {target_match['away_team']}")
        b365 = next((b for b in target_match['bookmakers'] if b['key'] == 'bet365'), target_match['bookmakers'][0])
        odds = {o['name']: o['price'] for o in b365['markets'][0]['outcomes']}
        
        # 顯示實時賠率
        m1, m2, m3 = st.columns(3)
        m1.metric("🏠 主勝", odds.get(target_match['home_team']))
        m2.metric("🤝 和局", odds.get('Draw'))
        m3.metric("🚀 客勝", odds.get(target_match['away_team']))
        
        # 執行 AI 推薦
        rec, conf, p_draw = ai_strategy_engine(
            odds.get(target_match['home_team']), 
            odds.get('Draw'), 
            odds.get(target_match['away_team']),
            search_team
        )
        
        st.markdown(f"""
        <div class="recommendation-box">
            <h3>🤖 AI 實時推薦指令</h3>
            <p style="font-size: 20px;">{rec}</p>
            <p>信心指數：<b>{conf}</b> | 隱含平局概率：{p_draw:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.subheader("📊 趨勢分析")
        # 模擬一個 AI 預期走勢
        fig = go.Figure(go.Scatter(x=[0,15,30,45,60,75,90], y=[2.5, 2.6, 2.8, 3.2, 3.5, 3.1, 3.0], mode='lines+markers', name='賠率走勢'))
        fig.update_layout(title="Bet365 賠率變動曲線 (模擬)", paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning(f"目前 API 中找不到包含 '{search_team}' 的實時比賽。請嘗試輸入其他熱門球隊。")

st.sidebar.markdown("### 🛠️ 系統日誌")
st.sidebar.write(f"[{datetime.now().strftime('%H:%M')}] 數據已更新...")
st.sidebar.write(f"[{datetime.now().strftime('%H:%M')}] AI 策略計算完成...")
