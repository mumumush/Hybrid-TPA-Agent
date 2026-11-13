import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.layer1_data.user_profile import UserProfile
from src.layer1_data.data_loader import generate_mock_ohlcv
from src.layer2_core_engine.swing_detector import detect_swing_points
from src.layer2_core_engine.supply_demand import calculate_supply_demand_zones
from src.layer2_core_engine.xgb_predictor import XGBWinRatePredictor
from src.layer3_reasoning.cot_planner import CoTPlanningAgent
from src.layer4_risk_output.risk_manager import RiskManager
from src.layer4_risk_output.report_generator import ReportGenerator

st.set_page_config(page_title="Hybrid TPA-Agent 決策儀表板", layout="wide", page_icon="📈")

st.title("📈 Hybrid TPA-Agent: 混合式短線交易智慧代理人系統")
st.caption("四層解耦架構：確定性空間幾何 + 防洩漏 XGBoost + CoT 價格行為推理 + 獨立風控否決閘門")

# 側邊欄：使用者風控偏好設定 (Layer 1.1)
st.sidebar.header("⚙️ Layer 1: 風險預算偏好")
account_capital = st.sidebar.number_input("帳戶資本 (USD)", min_value=1000.0, max_value=1000000.0, value=10000.0, step=1000.0)
risk_pct = st.sidebar.slider("單筆最大承受風險 (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.1) / 100.0
min_rr = st.sidebar.slider("最低風報比要求 (RR >=)", min_value=1.5, max_value=4.0, value=2.0, step=0.1)
min_win_rate = st.sidebar.slider("XGBoost 最小勝率門檻 (%)", min_value=45, max_value=70, value=55, step=1) / 100.0

st.sidebar.subheader("🚨 異常與熔斷模擬")
consecutive_losses = st.sidebar.number_input("今日連續虧損筆數", min_value=0, max_value=5, value=0)
api_latency = st.sidebar.number_input("API 傳輸延遲 (秒)", min_value=0.1, max_value=10.0, value=0.4, step=0.1)

# 載入資料 (Layer 1.2)
symbol = st.sidebar.selectbox("標的選擇", ["BTC/USDT", "ETH/USDT", "NVDA", "TSLA", "QQQ"])
bars_count = st.sidebar.slider("K 線長度", 60, 200, 100)

df = generate_mock_ohlcv(symbol=symbol, bars=bars_count)
user_profile = UserProfile(
    account_capital=account_capital,
    max_risk_pct=risk_pct,
    min_rr_threshold=min_rr,
    min_win_rate=min_win_rate
)

# Layer 2: 幾何與勝率
swings = detect_swing_points(df, window=5)
zones = calculate_supply_demand_zones(df, swing_window=5)
xgb = XGBWinRatePredictor(confidence_threshold=min_win_rate)

active_zone = zones[-1] if zones else None
current_price = df["close"].iloc[-1]
atr_val = df["atr_14"].iloc[-1]

if active_zone:
    win_rate, filter_passed, ml_meta = xgb.predict_conditional_win_rate(df, active_zone)
    cot_agent = CoTPlanningAgent()
    cot_data = cot_agent.generate_cot_reasoning(
        geometry_data={
            "zone_type": active_zone.zone_type,
            "upper": active_zone.upper_bound,
            "lower": active_zone.lower_bound,
            "is_sr_flip": active_zone.is_sr_flip
        },
        ml_data=ml_meta
    )
    
    # Layer 4: 風控評估
    rm = RiskManager(user_profile)
    risk_decision = rm.evaluate_trade(
        current_price=current_price,
        zone=active_zone,
        win_rate=win_rate,
        atr=atr_val,
        consecutive_losses=consecutive_losses,
        latency_seconds=api_latency
    )
    audit_card = ReportGenerator.generate_audit_card(symbol, risk_decision, cot_data, ml_meta)
else:
    st.warning("尚未偵測到成熟供需區結構。")
    st.stop()

# 繪製主視覺圖表 (Candlestick + S/D Zones)
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df["timestamp"],
    open=df["open"],
    high=df["high"],
    low=df["low"],
    close=df["close"],
    name="K 線行情"
))

# 標記供需區
for z in zones[-4:]:
    color = "rgba(46, 204, 113, 0.25)" if z.zone_type == "DEMAND" else "rgba(231, 76, 60, 0.25)"
    fig.add_shape(
        type="rect",
        x0=df["timestamp"].iloc[z.start_index],
        x1=df["timestamp"].iloc[-1],
        y0=z.lower_bound,
        y1=z.upper_bound,
        fillcolor=color,
        line=dict(width=1, color="green" if z.zone_type == "DEMAND" else "red")
    )

fig.update_layout(
    title=f"{symbol} 結構分析圖（帶供需區與幾何座標）",
    xaxis_rangeslider_visible=False,
    height=480,
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# 顯示四層流水線審計結果
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("當前行情市價", f"${current_price:,.2f}", f"ATR: {atr_val:.2f}")
with col2:
    st.metric("XGBoost 條件勝率", f"{win_rate*100:.1f}%", "濾網通過" if filter_passed else "未達門檻")
with col3:
    st.metric("風報比 (RR)", f"1 : {risk_decision.risk_reward_ratio:.2f}", f"門檻 >= {min_rr}")
with col4:
    st.metric("數學期望值 (E)", f"{risk_decision.mathematical_expectation:.3f}", "E > 0" if risk_decision.mathematical_expectation > 0 else "E <= 0")

st.markdown("---")

# 決策卡與人機協作
col_card, col_cot = st.columns([1, 1])

with col_card:
    st.subheader("🛡️ Layer 4: 風控審計決策卡")
    if risk_decision.status == "APPROVED":
        st.success(f"### ✅ 審核狀態：{risk_decision.status}")
    else:
        st.error(f"### 🛑 審核狀態：{risk_decision.status} (已啟動防護)")
        
    st.write(f"**審計裁定依據**：{risk_decision.reason}")
    if risk_decision.status == "APPROVED":
        st.write(f"• **建議進場位 (Entry)**: `${risk_decision.entry_price:,.2f}`")
        st.write(f"• **結構硬停損 (Stop-Loss)**: `${risk_decision.stop_loss:,.2f}`")
        st.write(f"• **目標停利位 (Take-Profit)**: `${risk_decision.take_profit:,.2f}`")
        st.write(f"• **計算建議部位**: `{risk_decision.position_size:.4f}` 單位 (最大風險 ${user_profile.get_max_loss_budget():,.2f})")
        st.button("👤 人類交易員最終確認下單 (Human-in-the-Loop)")
    else:
        st.info("系統已強制啟動保護機制，避免非理性交易或無效訊號暴露。")

with col_cot:
    st.subheader("🧠 Layer 3: CoT 思維鏈情境推理")
    st.markdown(f"**市場情境定性**: `{cot_data['market_regime']}`")
    st.markdown("**推理鏈過程**:")
    for step in cot_data["chain_of_thought"]:
        st.markdown(f"- {step}")
    st.markdown(f"**結構失效邊界**: `{cot_data['structural_invalidation']}`")
    st.caption("提示：LLM 不直接參與數值幾何運算，僅負責情境解讀與審查報告生成。")
