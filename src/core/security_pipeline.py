import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "src"))

try:
    from zones.zone_manager import ZoneManager
    from zones.zone_state import ZoneStateManager
    from zones.border_config import ZONES
except ImportError:
    from src.zones.zone_manager import ZoneManager
    from src.zones.zone_state import ZoneStateManager
    from src.zones.border_config import ZONES

try:
    from core.event_orchestrator import EventOrchestrator
except ImportError:
    from src.core.event_orchestrator import EventOrchestrator


class SecurityPipeline:
    """
    Coordinates zone detection, tracking state, intrusion detection,
    risk assessment, alert generation, and persistence.
    """

    def __init__(
        self,
        camera_id: str = "CAM-01",
        db_service: Optional[Any] = None,
        zones: Optional[list] = None,
        minimum_alert_severity: str = "MEDIUM",
        cooldown_seconds: float = 10.0,
    ) -> None:
        self.camera_id = camera_id
        if zones is None:
            zones = ZONES

        self.zone_manager = ZoneManager(zones)
        self.zone_state_manager = ZoneStateManager()
        self.orchestrator = EventOrchestrator(
            camera_id=camera_id,
            db_service=db_service,
            minimum_alert_severity=minimum_alert_severity,
            cooldown_seconds=cooldown_seconds,
        )

    def process_object(
        self,
        track_id: int,
        object_type: str,
        confidence: float,
        previous_zone: str,
        current_zone: str,
        direction: str,
        speed: float,
        dwell_time: float,
        timestamp: float,
    ) -> Dict[str, Optional[Any]]:
        """
        Process single tracked object.
        """
        res = self.orchestrator.process(
            track_id=track_id,
            object_type=object_type,
            confidence=confidence,
            previous_zone=previous_zone,
            current_zone=current_zone,
            direction=direction,
            speed=speed,
            dwell_time=dwell_time,
            timestamp=timestamp,
        )
        return res

    def process_frame(
        self,
        objects: list,
        timestamp: Optional[float] = None,
    ) -> List[Tuple[Any, Any, Any]]:
        """
        Process objects in a frame through zone manager and orchestrator.
        """
        if timestamp is None:
            timestamp = time.time()

        results = []
        for obj in objects:
            if not getattr(obj, "active", True):
                continue

            center = getattr(obj, "center", (getattr(obj, "x", 0), getattr(obj, "y", 0)))
            zone = self.zone_manager.get_zone(center)
            current_zone_name = zone.name if zone else None

            state = self.zone_state_manager.update(obj.track_id, current_zone_name, timestamp)
            dwell_time = self.zone_state_manager.get_dwell_time(obj.track_id, timestamp)

            vx = getattr(obj, "vx", 0.0)
            vy = getattr(obj, "vy", 0.0)
            direction = "DOWN" if vy > 0 else ("UP" if vy < 0 else "STATIONARY")
            speed = (vx**2 + vy**2) ** 0.5

            evt, rsk, alt = self.orchestrator.process_track(
                track_id=obj.track_id,
                object_type=getattr(obj, "object_type", "person"),
                confidence=getattr(obj, "confidence", 0.95),
                previous_zone=state.previous_zone,
                current_zone=state.current_zone,
                direction=direction,
                speed=speed,
                dwell_time=dwell_time,
                timestamp=timestamp,
            )

            if evt:
                results.append((evt, rsk, alt))

        return results

    def reset(self):
        self.zone_state_manager.states.clear()
        self.orchestrator.reset()
