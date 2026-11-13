from typing import Dict, Any
from .risk_manager import RiskDecision

class ReportGenerator:
    """
    模組 4.2: 輸出介面 (Structured Audit Report Generator)
    產生可審計、人機協作 (Human-in-the-Loop) 的結構化報告
    """
    @staticmethod
    def generate_audit_card(
        symbol: str,
        risk_decision: RiskDecision,
        cot_data: Dict[str, Any],
        ml_meta: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "title": f"Hybrid TPA-Agent 決策審計卡 - {symbol}",
            "decision_status": risk_decision.status,
            "metrics": {
                "entry_price": risk_decision.entry_price,
                "stop_loss": risk_decision.stop_loss,
                "take_profit": risk_decision.take_profit,
                "risk_reward_ratio": f"1:{risk_decision.risk_reward_ratio}",
                "expected_value_E": risk_decision.mathematical_expectation,
                "suggested_position_size": risk_decision.position_size,
                "win_rate_percentage": f"{ml_meta.get('win_rate', 0.5)*100:.1f}%"
            },
            "reasoning_evidence": {
                "market_regime": cot_data.get("market_regime", "N/A"),
                "chain_of_thought": cot_data.get("chain_of_thought", []),
                "invalidation_level": cot_data.get("structural_invalidation", "N/A")
            },
            "risk_governance": {
                "audit_verdict": risk_decision.reason,
                "circuit_breaker": risk_decision.circuit_breaker_active,
                "human_confirmation_required": True
            }
        }
