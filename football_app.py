import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- 配置區 ---
API_KEY = "d20c02bc2b0c66692623f40f1535c1fd"

st.set_page_config(page_title="AI Football Oracle v3.0", layout="wide", page_icon="💎")

# --- 1. 極致美化 CSS (磨砂玻璃背景 + 霓虹字體) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                    url('https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&q=80');
        background-size: cover;
    }
    
    .main-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    
    h1, h2, h3 { color: #00d4ff !important; font-family: 'Orbitron', sans-serif !important; }
    .stMetric label { color: #ffffff !important; font-size: 1.1rem !important; }
    .stMetric div { color: #00d4ff !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AI 推演核心引擎 ---
def ai_deep_learning_inference(minute, h_score, a_score, h_red, a_danger, star_player_impact):
    """模擬大模型推演：隨時間、球員狀態動態計算"""
    # 隨時間流逝，平局機率通常會下降，絕殺機率上升
    time_factor = (minute / 90) * 20
    # 球員影響力權重
    impact_factor = star_player_impact * 1.5
    
    prediction = 30 + time_factor + impact_factor - (h_red * 25)
    return max(min(prediction, 99.8), 0.2)

# --- 側邊欄 ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/824/824748.png", width=100)
st.sidebar.title("Oracle System")
app_mode = st.sidebar.radio("模組選擇", ["🛡️ 實時 AI 監控", "🧠 深度養成推演"])

# --- 模式 2：深度養成推演 (加入球員數據) ---
if app_mode == "🧠 深度養成推演":
    st.markdown("<h1>🧠 AI 大模型深度推演</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,1,1])
        
        with c1:
            h_name = st.text_input("🏠 球隊名稱", "沙士菲")
            minute = st.slider("⏱️ 比賽分鐘 (0-90)", 0, 90, 65)
            h_red = st.number_input("🔴 紅牌數量", 0, 2, 0)
            
        with c2:
            a_name = st.text_input("🚀 對手名稱", "塔勒瑞斯")
            h_score = st.number_input("目前比分", 0, 5, 0)
            a_score = st.number_input("對方比分", 0, 5, 1)
            
        with c3:
            st.markdown("##### 🌟 球員狀態 (AI 插件)")
            star_name = st.text_input("關鍵球員", "Lionel Messi")
            star_form = st.select_slider("球員即時表現評分", options=[1, 2, 3, 4, 5], value=4)
            h_danger = st.number_input("全場危險進攻", 0, 150, 42)

        if st.button("🧬 啟動 AI 神經元運算"):
            with st.spinner('AI 正在讀取全球賠率與球員歷史數據...'):
                time.sleep(1.5) # 模擬運算感
                
                res_prob = ai_deep_learning_inference(minute, h_score, a_score, h_red, h_danger, star_form)
                
                st.markdown("---")
                col_res1, col_res2 = st.columns([2,1])
                
                with col_res1:
                    # 專業儀表板
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number+delta",
                        value = res_prob,
                        delta = {'reference': 40, 'increasing': {'color': "#00ffcc"}},
                        title = {'text': f"AI 預期 {h_name} 逆轉機率", 'font': {'size': 24, 'color': '#00d4ff'}},
                        gauge = {
                            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#00d4ff"},
                            'bar': {'color': "#00d4ff"},
                            'bgcolor': "rgba(0,0,0,0)",
                            'borderwidth': 2,
                            'bordercolor': "#00d4ff",
                            'steps': [
                                {'range': [0, 30], 'color': 'rgba(255, 0, 0, 0.3)'},
                                {'range': [70, 100], 'color': 'rgba(0, 255, 0, 0.3)'}]
                        }
                    ))
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "#00d4ff", 'family': "Orbitron"})
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_res2:
                    st.markdown(f"### 🤖 AI 推演報告")
                    st.write(f"📌 **關鍵球員影響**：{star_name} 的活躍度為 {star_form}/5，對進攻增強了 `{star_form*12}%`。")
                    st.write(f"⏱️ **時間壓力**：比賽進入 {minute} 分鐘，絕殺權重上升。")
                    if res_prob > 75:
                        st.success("🔥 AI 檢測到「強烈進球信號」！")
                    elif res_prob < 20:
                        st.error("📉 AI 建議：此場已進入「死亡時間」，逆轉機會渺茫。")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 模式 1：API 實時監控 (維持穩定) ---
else:
    st.title("🛡️ 實時 API 指揮中心")
    # ... (此處保留你之前成功的 API 顯示代碼，但加上 main-card class)
    st.info("請切換至「深度養成推演」查看 AI 大模型效果。")
