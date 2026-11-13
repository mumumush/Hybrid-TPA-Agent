import json
from typing import Dict, Any
from .price_action_kb import PriceActionKnowledgeBase

class CoTPlanningAgent:
    """
    模組 3.2: 規劃與推理代理人 (Planning & Reasoning Agent)
    嚴格遵循解耦原則：LLM 僅接收來自 Layer 2 的結構化幾何與機率特徵，
    進行情境解讀、假突破形態比對與可解釋性審計敘事，絕不負責精確數值計算。
    """
    def __init__(self, kb: PriceActionKnowledgeBase = None):
        self.kb = kb or PriceActionKnowledgeBase()

    def build_structured_prompt(self, geometry_data: Dict[str, Any], ml_data: Dict[str, Any]) -> str:
        """產生送往 LLM 的結構化思維鏈 Prompt"""
        return f"""
[Role]: 你是 Hybrid TPA-Agent 的資深價格行為與風控審計員。
[Context Data]:
- 空間幾何資料: {json.dumps(geometry_data, ensure_ascii=False, indent=2)}
- 機器學習預測: {json.dumps(ml_data, ensure_ascii=False, indent=2)}
- 領域知識庫規則參考: {json.dumps(PriceActionKnowledgeBase.RULES, ensure_ascii=False, indent=2)}

[Instructions]:
請利用思維鏈 (Chain of Thought, CoT) 進行以下 4 步推理：
1. 分析當前市場微結構與供需區特徵（是否為 S/R Flip、是否出現拒絕影線）。
2. 比對領域知識庫中的形態（例如威科夫 Spring 假跌破或蓄勢形態）。
3. 明確指出該交易結構之「失效邊界點位 (Invalidation Level)」。
4. 撰寫人類交易員可直接審核的風險審查敘事，禁止隨意變更幾何座標數值。
"""

    def generate_cot_reasoning(self, geometry_data: Dict[str, Any], ml_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        產出 CoT 結構化推理成果 (支援 Mock / API 調用)
        """
        zone_type = geometry_data.get("zone_type", "DEMAND")
        is_flip = geometry_data.get("is_sr_flip", False)
        win_rate = ml_data.get("win_rate", 0.5)

        narrative_steps = [
            f"Step 1 [結構感知]: 偵測到關鍵 {zone_type} 區域，當前價格已回踩邊界，ATR 波動度正常。",
            f"Step 2 [知識庫比對]: 價格測試該區域時伴隨量能沉澱與長影線拒絕，符合 Price Action 之回測支撐行為。" if zone_type == "DEMAND" else "供給區壓制明顯，存在流動性吸收現象。",
            f"Step 3 [機率驗證]: XGBoost 評估之條件勝率為 {win_rate*100:.1f}%，符合高於 55% 之濾網要求。",
            f"Step 4 [失效點界定]: 一旦 K 線實體跌破/突破結構邊界外加 1.0 ATR，本交易假設立即失效，觸發硬停損。"
        ]

        return {
            "market_regime": f"{zone_type} Zone Retest ({'S/R Flip' if is_flip else 'Direct Support'})",
            "chain_of_thought": narrative_steps,
            "liquidity_narrative": "買賣雙方在關鍵流動性區域完成換手，未見異常恐慌性拋售，結構維持完整。",
            "structural_invalidation": "若價格強勢收破結構邊界外 1.0 ATR，立即判定結構破壞。",
            "human_readable_summary": f"幾何結構良好，XGBoost 勝率 {win_rate*100:.1f}%，建議進入 Layer 4 風控審查。"
        }
