# Hybrid TPA-Agent: 系統架構與設計規格書 (DESIGN.md)

## 1. 系統概述 (System Overview)

Hybrid TPA-Agent（混合式短線交易智慧代理人系統）針對散戶短線交易中面臨之「高頻摩擦成本、空間結構忽視、情緒化過度交易與純 LLM 數值幻覺」等痛點，提出**確定性演算法（幾何精確）+ 機器學習（條件機率）+ LLM Agent（情境推理）+ 獨立風控（否決機制）**之四層解耦架構。

本系統明確將目標定位為：**在嚴格風控與可解釋性下，輔助交易者降低情緒化與無效訊號暴露，實現正期望值決策**，而非宣稱自動化穩定獲利。

---

## 2. 四層八模組架構設計 (4 Layers & 8 Modules)

### 2.1 Layer 1: 輸入與資料層 (Input & Data Ingestion Layer)
* **模組 1.1: 使用者偏好模組 (User Preferences Module)**
  * **輸入**：使用者指定之帳戶本金（Capital）、單筆最大風險百分比（Risk% 如 1.0%）、交易時區、允許交易之標的清單。
  * **職責**：建立使用者風險輪廓（Risk Profile），設定部位上限與停損金額門檻。
* **模組 1.2: 資料接收引擎 (Data Ingestion Engine)**
  * **輸入**：歷史與即時多時間框架 OHLCV 串流（1H / 15M / 5M），包含成交量分佈（Volume Profile）。
  * **職責**：數據清洗、缺失值補齊、時間對齊與防洩漏時間序列排序（Strict Timestamp Indexing）。

### 2.2 Layer 2: 核心分析引擎 (Core Analysis Engine)
* **模組 2.1: 供需區算術引擎 (Supply & Demand Arithmetic Engine)**
  * **職責**：純確定性 Python 幾何計算，100% 可重現，徹底杜絕 LLM 空間幻覺。
  * **演算法**：
    1. 計算 $N$ 根 K 線的局部波段高點（Swing High）與波段低點（Swing Low）：
       $$\text{Swing High}_t = \max(P_{t-k}, \dots, P_{t+k})$$
    2. 基於大實體推進 K 線（Momentum Candles）起點計算未回測供需區（Unmitigated Zones）：
       $$\text{Demand Zone} = [\text{Low}_{\text{base}}, \max(\text{Open}_{\text{base}}, \text{Close}_{\text{base}})]$$
    3. 偵測支撐壓力互換（S/R Flip）：原本供給區被強勢實體 K 線突破後，自動標記為潛在候選支撐區。
* **模組 2.2: 勝率預測引擎 (Win-Rate Prediction Engine)**
  * **演算法**：XGBoost 梯度提升決策樹分類器。
  * **特徵矩陣**：
    * $\text{Dist}_{\text{zone}}$：當前價格距供需區邊界的相對百分比
    * $\text{ATR}_{\text{ratio}}$：當前 K 線實體與 ATR(14) 之比值
    * $\text{Vol}_{\text{zscore}}$：成交量相對 20 期均值之 Z-score
    * $\text{Wick}_{\text{ratio}}$：引線長度與實體之比值（拒絕形態量化）
    * $\text{Session}$：當前市場時段（美股開盤、倫敦開盤、亞洲盤）
  * **門檻過濾**：僅當條件勝率 $W \ge 0.55$ 時，訊號才傳遞至 Layer 3；低於門檻直接標記為 `LOW_CONFIDENCE` 並中止流水線。

### 2.3 Layer 3: 推理與領域知識層 (Reasoning & Domain Knowledge Layer)
* **模組 3.1: 價格行為領域知識庫 (Domain Knowledge Base)**
  * **內容**：策展過的可執行 Price Action 規則庫：
    * 假突破（Liquidity Sweep / Spring / Upthrust）辨識準則
    * 突破前回測（Pre-breakout build-up）與回測確認（Post-breakout retest）
    * 多時間框架（MTF）趨勢共振條件
* **模組 3.2: 規劃與推理代理人 (Planning & Reasoning Agent)**
  * **機制**：將 Layer 2 輸出的結構化幾何座標與 XGBoost 機率封裝為標準 JSON，透過思維鏈（Chain of Thought, CoT）進行結構推理。
  * **規範**：**LLM 不執行任何加減乘除或座標推算**，僅針對已知確定性特徵撰寫推理邏輯、市場情境背景與潛在失效場景（Failure Modes）。

### 2.4 Layer 4: 風險管理與輸出層 (Risk Management & Output Layer)
* **模組 4.1: 決策與風控引擎 (Decision & Risk Control Engine)**
  * **職責**：擁有最高決策否決權（Veto Power）。
  * **三道強制審查閘門**：
    1. **風報比檢驗**：$RR = \frac{|\text{Target} - \text{Entry}|}{|\text{Entry} - \text{StopLoss}|} \ge 2.0$
    2. **正期望值檢驗**：$E = W \times RR - (1 - W) > 0$
    3. **波動度動態停損**：停損點設於結構邊界外加 $1.0 \times \text{ATR}$
  * **三級安全熔斷機制**：
    * Level 1（波動激增）：ATR 激增 > 2.5 倍時，倉位減半、提高 RR 要求。
    * Level 2（連續虧損）：單日 2 連敗或回撤達 3%，當日全線禁止開倉。
    * Level 3（連線異常）：數據延遲 > 5 秒，啟動全單保護與唯讀鎖定。
* **模組 4.2: 輸出介面 (User-Facing Interface)**
  * 產生符合審計標準的完整交易提案（Audit Card）：
    * 決策狀態（`APPROVED` / `WAIT` / `NO_TRADE`）
    * 具體點位（Entry, Stop-Loss, Take-Profit 1, Take-Profit 2）
    * 建議手數（Lot / Share Size）
    * CoT 推理證據鏈與否決原因說明。

---

## 3. 資料交換介面規格 (Data Exchange Contracts)

```json
{
  "signal_id": "SIG-20261113-BTC-001",
  "symbol": "BTC/USDT",
  "timeframe": "15m",
  "timestamp": "2026-11-13T14:30:00Z",
  "geometry": {
    "swing_high": 98500.0,
    "swing_low": 96200.0,
    "zone_type": "DEMAND",
    "zone_upper": 96600.0,
    "zone_lower": 96250.0,
    "is_sr_flip": true,
    "atr_14": 350.0
  },
  "ml_assessment": {
    "model": "XGBoost-v2",
    "win_rate_probability": 0.635,
    "confidence_passed": true
  },
  "risk_assessment": {
    "proposed_entry": 96650.0,
    "hard_stop_loss": 96150.0,
    "take_profit_target": 98200.0,
    "risk_reward_ratio": 3.10,
    "mathematical_expectation": 0.968,
    "position_size": 0.42,
    "status": "APPROVED"
  },
  "llm_cot_reasoning": {
    "market_regime": "Uptrend Pullback to Key S/R Flip Zone",
    "liquidity_narrative": "Demand zone successfully absorbed sell volume with strong lower wick rejection.",
    "failure_scenario": "Break and close below 96,150 invalidates structure.",
    "human_action_required": "Confirm manual execution upon candle close above 96,650."
  }
}
```

---

## 4. 回測與評估協議 (Walk-Forward Backtesting Protocol)

1. **資料範圍**：長週期多資產池（含大型權值股、主要加密貨幣、指數 ETF）。
2. **滾動分割**：使用 6 個月滑動窗口訓練 XGBoost，1 個月驗證超參數，隨後於次月進行未見資料測試。
3. **交易摩擦模擬**：每筆扣除標準手續費（5 bps）及可變滑價（5~15 bps）。
4. **輸出統計**：回測產生權益曲線（Equity Curve）、水下圖（Underwater Plot）及每月績效熱力圖。
