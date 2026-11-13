# Hybrid TPA-Agent: 混合式短線交易智慧代理人系統
## 資訊圖表規格書（A4 橫式・高密度 NUMBERING 系統架構藍圖）

---

### [01] 核心問題與實證數據痛點 (Empirical Evidence & The Day-Trading Reality)

* **1.1 散戶短線交易的結構性困境**
  * **1.1.1 巴西期貨當沖 300 天實證研究**：追蹤 1,551 位持續交易逾 300 天的個人當沖客，實證發現 **97% 最終虧損**；僅 1.1% 獲利超過巴西法定最低工資，僅 0.5% 超過銀行櫃員起薪。未發現隨交易經驗增加而提高獲利機率之學習效應（Chague et al., SSRN 2019）。
  * **1.1.2 FINRA 監管警告 (Rule 2270 / Notice 24-13)**：短線交易面臨極端本金虧損風險，高頻摩擦成本、流動性驟降與技術系統故障（API 中斷）是導致非預期爆倉的主因。
  * **1.1.3 摩擦成本黑洞測算**：以單筆交易成本（手續費+滑價）16 美元、日均 29 筆試算，年化需賺取 **$111,360 美元毛利** 僅供支付手續費。高頻訊號不等於正期望值。
* **1.2 現有主流方法之三大短板與研究缺口 (Research Gap)**
  * **1.2.1 傳統量化與純 ML 模型 (MA, RSI, XGBoost)**：指標具本質滯後性；忽視圖表幾何與「空間結構」，盤整期與假突破震盪產出大量雜訊。
  * **1.2.2 純大型語言模型 (LLM Trading Agents)**：具備強大文字情境推理，但數值精度低、嚴重缺乏空間幾何辨別力，易產生「空間與數值幻覺」，導致部位計算錯誤（arXiv:2605.19337）。
  * **1.2.3 靜態技術支撐壓力工具 (KDE, Pivot Points)**：僅能靜態畫線，缺乏後續突破/反彈條件機率量化與動態風險報酬比評估。

---

### [02] 混合架構理念與功能解耦 (Hybrid Decoupling Philosophy)

* **2.1 核心原則：「讓每個元件只做它最擅長的事」**
  * **2.1.1 確定性演算法 (Deterministic Python)** $\rightarrow$ **100% 空間幾何精確**：波段高低點（Swing High/Low）、供需區邊界座標、ATR 波動度，完全杜絕 LLM 空間幻覺。
  * **2.1.2 機器學習 (XGBoost Classifier)** $\rightarrow$ **客觀條件機率評估**：嚴格 Walk-forward 條件下，輸出突破/反彈勝率 $W$。
  * **2.1.3 大型語言模型 (LLM Agent + CoT)** $\rightarrow$ **語意推理與敘事審查**：接收結構化 JSON，結合 Price Action 領域知識進行思維鏈推理，產出人類可審計報告。
  * **2.1.4 獨立風控引擎 (Deterministic Risk Gate)** $\rightarrow$ **最高否決權 (Veto Power)**：強制執行硬停損、風報比門檻及正期望值檢驗，必要時輸出 `NO_TRADE`。

---

### [03] 四層八模組決策管線 (4-Layer 8-Module System Architecture)

```
[ L1: 資料與偏好層 ]
  ├── 1.1 使用者偏好模組 (Risk Profile, Max Capital, Risk/Trade)
  └── 1.2 資料接收引擎 (OHLCV Stream, Volume Distribution, Orderflow)
          │
          ▼
[ L2: 核心分析引擎 ]
  ├── 2.1 供需區算術引擎 (Swing High/Low, Zone Bounds, S/R Flip)
  └── 2.2 勝率預測引擎 (XGBoost: W >= 55% 條件機率門檻過濾)
          │ [通過條件勝率門檻]
          ▼
[ L3: 推理與知識層 ]
  ├── 3.1 領域知識庫 (Price Action Rules, Fake-out Patterns, Liquidity Sweeps)
  └── 3.2 規劃與推理代理人 (LLM CoT 推理, 生成結構化交易情境論證)
          │
          ▼
[ L4: 風控與輸出層 ]
  ├── 4.1 決策與風控引擎 (ATR 動態停損, RR >= 2.0, 期望值 E > 0, 熔斷降級)
  └── 4.2 輸出介面 (APPROVED 交易卡 / NO_TRADE 防護, 審計報告, Streamlit UI)
```

* **3.1 模組編號與功能職責**
  * `[MOD 1.1]` **使用者偏好模組**：設定單筆最大風險百分比（如 1%~2%）、最大槓桿倍數。
  * `[MOD 1.2]` **資料接收引擎**：抓取歷史與即時多時間框架 K 線（1H / 15M / 5M），計算 Volume Profile。
  * `[MOD 2.1]` **供需區算術引擎**：以幾何演算法識別未測試之供需區（Unmitigated Supply/Demand Zone）及支撐壓力互換位（S/R Flip）。
  * `[MOD 2.2]` **勝率預測引擎**：特徵工程（距離供需區距離、ATR 比值、K 線形態、時段特徵），由 XGBoost 評估突破/反彈勝率 $W$。
  * `[MOD 3.1]` **價格行為領域知識庫**：策展規則庫，規範假突破（Spring / Upthrust）與回測結構特徵。
  * `[MOD 3.2]` **規劃推理代理人**：以 CoT（Chain of Thought）比對即時特徵與知識庫，評估市場情境並產出推論摘要。
  * `[MOD 4.1]` **決策與風控引擎**：嚴格計算進場點、結構失效停損點、目標停利點與期望值 $E$。
  * `[MOD 4.2]` **互動輸出介面**：產出包含完整證據鏈與止損止盈座標之可執行報告。

---

### [04] 數理公式與硬風控閘門 (Mathematical Rigor & Risk Gates)

* **4.1 核心數學模型**
  * **4.1.1 數學期望值公式 (Mathematical Expectation)**：
    $$E = W \times RR - (1 - W)$$
    *系統硬性規定：僅在 $E > 0$ 且滿足安全邊際時允許輸出 `APPROVED`；若 $E \le 0$ 強制退回 `NO_TRADE`。*
  * **4.1.2 風險報酬比 (Risk-to-Reward Ratio)**：
    $$RR = \frac{|\text{Target Price} - \text{Entry Price}|}{|\text{Entry Price} - \text{Stop Loss Price}|} \ge 2.0$$
  * **4.1.3 動態停損計算 (ATR-based Dynamic Stop-Loss)**：
    $$\text{Stop Loss}_{\text{Long}} = \min(\text{Zone Bottom}, \text{Swing Low}) - \alpha \times \text{ATR}_{14} \quad (\alpha \in [0.5, 1.2])$$
  * **4.1.4 倉位部位控管 (Position Sizing by Risk Budget)**：
    $$\text{Position Size} = \frac{\text{Account Equity} \times \text{Max Risk \%}}{|\text{Entry Price} - \text{Stop Loss Price}|}$$

* **4.2 三級安全降級與熔斷協議 (Three-Tier Circuit Breaker)**
  * **4.2.1 Level 1（波動度激增）**：當即時 ATR 超過歷史 30 日中位數 2.5 倍時，自動降低倉位 50%，RR 門檻提高至 2.5。
  * **4.2.2 Level 2（連續虧損防禦）**：當日連續觸發 2 筆停損或單日回撤達 3%，系統當日全面鎖定為 `NO_TRADE`。
  * **4.2.3 Level 3（API/流動性異常）**：數據源延遲超過 5 秒或價差擴大逾 3 倍時，強制取消現有待成交委託，全面轉為唯讀監控模式。

---

### [05] 嚴格評估與 Walk-Forward 實驗矩陣 (Empirical Validation Matrix)

* **5.1 實驗防洩漏協議 (Anti-Leakage Protocol)**
  * **5.1.1 滾動時間序列驗證 (Walk-Forward Validation)**：嚴格依時間先後劃分 Training (60%) / Validation (20%) / Testing (20%)，嚴禁隨機切分（Random Shuffle）。
  * **5.1.2 特徵標準化隔離**：標準化參數（Mean / Std / MinMax）僅於過去訓練窗口計算，禁止未來資訊窺探（No Look-ahead Bias）。
* **5.2 六大多維對照基準 (Baseline Comparison)**
  * `[BL-1]` **被動持有基準 (Buy-and-Hold)**：檢驗短線決策是否具備超越 Beta 的實質 Alpha。
  * `[BL-2]` **隨機進出場對照 (Random Signals with Same RR)**：驗證幾何結構訊號是否具備超越隨機擲幣的資訊含量。
  * `[BL-3]` **傳統趨勢策略 (MA Dual Crossover)**：對照典型滯後指標策略。
  * `[BL-4]` **傳統震盪策略 (RSI Overbought/Oversold)**：對照典型盤整反轉指標。
  * `[BL-5]` **純機器學習模型 (XGBoost Only)**：檢驗是否加入 Price Action 空間特徵與 CoT 審查帶來邊際增益。
  * `[BL-6]` **純大型語言模型 (LLM Only)**：檢驗未解耦之 LLM 在數值運算與空間辨別上的幻覺退化現象。
* **5.3 核心評估指標矩陣 (Evaluation Metrics)**
  * **風險調整後績效**：Sharpe Ratio, Sortino Ratio, Calmar Ratio, 最大回撤 (MDD)。
  * **交易品質與期望值**：實際淨勝率 $W_{\text{net}}$、實現盈虧比 $RR_{\text{realized}}$、扣除手續費滑價後之淨期望值 $E_{\text{net}}$。
  * **摩擦成本敏感度測試**：在滑價 0 bp, 5 bp, 10 bp, 20 bp 梯度下之淨收益曲線衰退分析。
  * **統計顯著性檢驗**：White's Reality Check 與 Bootstrap 區間估計（95% CI）。

---

### [06] 專案成果產出與可解釋性審計 (Deliverables & Interpretability)

* **6.1 模組化開源程式碼套件**：高內聚、低耦合的 Python 專案架構（四層分離，含單元測試與回測模組）。
* **6.2 Streamlit 互動決策儀表板**：提供 K 線供需區視覺化、XGBoost 條件機率即時評估、CoT 審查報告及風控按鈕。
* **6.3 人機協作（Human-in-the-Loop）審計交易卡範例**：
  * **狀態標籤**：`APPROVED` (或 `WAIT` / `NO_TRADE`)
  * **幾何座標**：進場點 100.00 / 停損點 97.50 / 第一目標 106.00 (RR = 2.40)
  * **機器學習指標**：條件突破勝率 $W = 62.4\%$，期望值 $E = 1.12 > 0$
  * **CoT 推理結論**：4H 級別需求區第三次帶量回測，下影線長度 > 實體 1.5 倍，符合 S/R Flip 支撐確認，風控審查核准。
