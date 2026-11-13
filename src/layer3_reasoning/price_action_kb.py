from typing import Dict, List

class PriceActionKnowledgeBase:
    """
    模組 3.1: 價格行為領域知識庫 (Domain Knowledge Base)
    包含可執行的 Price Action 規則、S/R Flip 條件、流動性陷阱與結構失效準則
    """
    RULES: Dict[str, Dict[str, str]] = {
        "SR_FLIP": {
            "name": "支撐壓力互換法則 (S/R Flip)",
            "condition": "原關鍵需求區遭有效帶量擊破後，當價格反彈至該區邊界時，觀察是否出現上影線或回測停滯，視為候選壓力轉換。",
            "invalidation": "若實體 K 線強勢收回原區域上方超過 1.0 ATR，則互換假設失效。"
        },
        "SPRING_FALSE_BREAKOUT": {
            "name": "威科夫彈簧假跌破 (Spring Pattern)",
            "condition": "價格短暫跌破波段低點或需求區下緣，隨即爆量收出長下影線（下影線長度 >= 實體 1.5 倍）並重回區間內。",
            "trade_intent": "流動性獵殺完成，為潛在做多回測進場機會。"
        },
        "UPTHRUST_FALSE_BREAKOUT": {
            "name": "上衝假突破 (Upthrust Pattern)",
            "condition": "價格短暫刺破波段高點或供給區上緣，伴隨長上影線與成交量萎縮，隨後陰線吞沒。",
            "trade_intent": "買盤力竭，為潛在做空回測機會。"
        },
        "PRE_BREAKOUT_BUILDUP": {
            "name": "突破前密集蓄勢 (Buildup)",
            "condition": "價格緊貼阻力或支撐區呈現 ATR 波動度收斂與較高低點（Higher Lows），預告高機率真突破。",
            "trade_intent": "順勢突破掛單準備。"
        }
    }

    @classmethod
    def get_rule_summary(cls) -> List[str]:
        return [f"[{k}] {v['name']}: {v['condition']}" for k, v in cls.RULES.items()]
