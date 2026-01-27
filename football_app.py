import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="足球指揮中心 v1.0", page_icon="⚽", layout="wide")

def get_live_data():
    return {
        "home": "沙士菲 (Vélez)",
        "away": "塔勒瑞斯 (Talleres)",
        "score": "0 - 1",
        "minute": 52,
        "possession_h": 58,
        "dangerous_attacks_h": 27,
        "bet365_draw_odds": 2.15
    }

data = get_live_data()
st.title("⚽ 足球指揮中心：全球實時演算")
st.write(f"最後更新：{datetime.now().strftime('%H:%M:%S')}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("當前比分", data["score"])
col2.metric("比賽分鐘", f"{data['minute']}'")
col3.metric("沙士菲控球", f"{data['possession_h']}%")
col4.metric("Bet365 平局賠率", data["bet365_draw_odds"], "-0.15")

st.subheader("🔮 實時進球/絕殺概率推演")
win_prob = 35 
if data["possession_h"] > 55: win_prob += 10
if data["bet365_draw_odds"] < 2.5: win_prob += 12

fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = win_prob,
    title = {'text': "沙士菲扳平機率 (%)"},
    gauge = {'axis': {'range': [None, 100]},
             'steps': [{'range': [0, 50], 'color': "lightgray"},
                       {'range': [50, 80], 'color': "skyblue"},
                       {'range': [80, 100], 'color': "royalblue"}]}))
st.plotly_chart(fig, use_container_width=True)

st.error("🚨 **Bet365 異動警報**：平局賠率劇烈下壓，市場預期沙士菲即將入球！")
