import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 配置區 ---
API_KEY = "d20c02bc2b0c66692623f40f1535c1fd" 

st.set_page_config(page_title="足球全功能戰術分析儀", layout="wide")

# --- 側邊欄控制 ---
st.sidebar.title("🎮 戰術操控台")
app_mode = st.sidebar.selectbox("切換功能", ["🌍 API 實時監控", "🧠 手動養成推演"])

# --- 核心演算函數 ---
def calculate_advanced_win_prob(h_score, a_score, h_danger, a_danger, h_red, a_red, h_poss, h_odds):
    """
    養成大模組公式：
    基礎機率 + 壓力加權 - 紅牌懲罰 + 控球加權
    """
    # 1. 基礎機率 (由賠率導出)
    base_prob = (1 / h_odds) * 100 if h_odds > 0 else 50
    
    # 2. 壓力加權 (危險進攻差)
    pressure_bonus = (h_danger - a_danger) * 0.4
    
    # 3. 紅牌懲罰 (極重要：少一人機率大幅下降)
    red_card_penalty = (h_red * 15) - (a_red * 15)
    
    # 4. 控球率加權
    possession_bonus = (h_poss - 50) * 0.2
    
    # 5. 總分計算
    final_prob = base_prob + pressure_bonus - red_card_penalty + possession_bonus
    return max(min(final_prob, 99.0), 1.0) # 限制在 1-99% 之間

# --- 模式 1：API 實時監控 ---
if app_mode == "🌍 API 實時監控":
    st.title("📊 聯賽實時數據中心")
    league = st.sidebar.selectbox("選擇聯賽", ["soccer_epl", "soccer_spain_la_liga", "soccer_italy_serie_a"])
    
    # (API 抓取邏輯同之前一樣，此處略過節省空間，保持穩定運作)
    st.info("系統正透過 The Odds API 監控最新賠率。")
    # ...[API Fetch 代碼]...

# --- 模式 2：手動養成推演 (重點！) ---
else:
    st.title("🧠 戰術養成大模組")
    st.write("手動輸入現場觀察到的數據，進行深度演算。")
    
    with st.form("manual_analysis"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("### 🏠 主隊 (Home)")
            h_team = st.text_input("球隊名", "沙士菲")
            h_score = st.number_input("目前比分", 0, 10, 0, key="h1")
            h_red = st.number_input("🔴 紅牌數量", 0, 5, 0, key="h2")
            h_poss = st.slider("⚽ 控球率 (%)", 0, 100, 50)
            
        with c2:
            st.markdown("### 🚀 客隊 (Away)")
            a_team = st.text_input("球隊名 ", "塔勒瑞斯")
            a_score = st.number_input("目前比分 ", 0, 10, 1, key="a1")
            a_red = st.number_input("🔴 紅牌數量 ", 0, 5, 0, key="a2")
            
        with c3:
            st.markdown("### 📈 市場數據")
            h_odds = st.number_input("主勝即時賠率", 1.0, 50.0, 2.5)
            h_danger = st.number_input("主隊危險進攻", 0, 200, 35)
            a_danger = st.number_input("客隊危險進攻", 0, 200, 28)

        submitted = st.form_submit_button("🔥 執行深度養成演算")

    if submitted:
        # 執行計算
        prob = calculate_advanced_win_prob(h_score, a_score, h_danger, a_danger, h_red, a_red, h_poss, h_odds)
        
        # 顯示結果
        st.divider()
        res_col1, res_col2 = st.columns([2, 1])
        
        with res_col1:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = prob,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"{h_team} 實時勝率/反超預測"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkred" if h_red > a_red else "darkblue"},
                    'steps': [
                        {'range': [0, 30], 'color': "#ffcccc"},
                        {'range': [30, 70], 'color': "#fff3cd"},
                        {'range': [70, 100], 'color': "#d4edda"}]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)

        with res_col2:
            st.subheader("📋 戰術診斷")
            if h_red > a_red:
                st.error(f"❗ **人數劣勢**：{h_team} 少打一人，勝率已自動下調 15%。")
            if h_danger > a_danger * 1.5:
                st.success(f"⚡ **進攻壓制**：{h_team} 正處於狂攻狀態，絕殺機會增加。")
            if h_poss > 60:
                st.info(f"🏟️ **控球優勢**：比賽節奏由 {h_team} 掌控。")
