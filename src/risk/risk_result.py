from dataclasses import dataclass


@dataclass
class RiskResult:
    """
    Result produced by the risk engine.
    """

    score: float

    severity: str

    breakdown: dict
