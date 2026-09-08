from dataclasses import dataclass


@dataclass
class Alert:
    """
    Represents a system alert generated
    from an intrusion event and risk result.
    """

    alert_id: str

    event_id: str

    timestamp: float

    camera_id: str

    track_id: int

    object_type: str

    message: str

    severity: str

    risk_score: float

    acknowledged: bool = False
