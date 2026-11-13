from dataclasses import dataclass

@dataclass
class UserProfile:
    """
    模組 1.1: 使用者偏好模組
    定義交易帳戶資本、單筆承受風險百分比與硬性風險上限
    """
    account_capital: float = 10000.0   # 初始帳戶資本 (USD)
    max_risk_pct: float = 0.01         # 單筆交易最大虧損比例 (1%)
    max_daily_loss_pct: float = 0.03   # 單日最大虧損熔斷比例 (3%)
    min_rr_threshold: float = 2.0      # 最小風報比門檻 (RR >= 2.0)
    min_win_rate: float = 0.55         # XGBoost 最小條件勝率門檻 (55%)
    max_leverage: float = 5.0          # 最大允許槓桿

    def get_max_loss_budget(self) -> float:
        """計算單筆允許的最大風險金額"""
        return self.account_capital * self.max_risk_pct
