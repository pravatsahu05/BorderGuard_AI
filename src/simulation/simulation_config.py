from dataclasses import dataclass, field
from typing import Dict, Any

SIMULATION_CONFIG = {
    "camera_id": "SIM-CAM-01",
    "width": 960,
    "height": 540,
    "time_scale": 1.0,
    "minimum_alert_severity": "MEDIUM",
    "default_scenario": "restricted_crossing",
}


@dataclass
class SimulationConfig:
    """
    Configuration parameters for software border simulation.
    """
    scenario_name: str = "restricted_crossing"
    time_scale: float = 1.0
    fps: float = 30.0
    camera_id: str = "SIM-CAM-01"
    db_path: str = "data/database/borderguard.db"
    reset_db: bool = False
    minimum_alert_severity: str = "MEDIUM"
    dedup_cooldown: float = 10.0
    max_frames: int = 150
    width: int = 960
    height: int = 540

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_name": self.scenario_name,
            "time_scale": self.time_scale,
            "fps": self.fps,
            "camera_id": self.camera_id,
            "db_path": self.db_path,
            "reset_db": self.reset_db,
            "minimum_alert_severity": self.minimum_alert_severity,
            "dedup_cooldown": self.dedup_cooldown,
            "max_frames": self.max_frames,
            "width": self.width,
            "height": self.height,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
