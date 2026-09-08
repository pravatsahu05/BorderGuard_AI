import sys
import time
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "src"))
sys.path.append(str(BASE_DIR / "data" / "database"))

try:
    from intrusion.intrusion_engine import IntrusionEngine
    from intrusion.deduplication import EventDeduplicator
except ImportError:
    from src.intrusion.intrusion_engine import IntrusionEngine
    from src.intrusion.deduplication import EventDeduplicator

try:
    from risk.risk_engine import RiskEngine
except ImportError:
    from src.risk.risk_engine import RiskEngine

try:
    from alerts.alert_engine import AlertEngine
except ImportError:
    from src.alerts.alert_engine import AlertEngine

try:
    from core.event_summary import EventSummary
    from core.event_formatter import EventFormatter
except ImportError:
    from src.core.event_summary import EventSummary
    from src.core.event_formatter import EventFormatter

try:
    from database_service import DatabaseService
except ImportError:
    try:
        from data.database.database_service import DatabaseService
    except ImportError:
        from src.database.database_service import DatabaseService


class EventOrchestrator:
    """
    Coordinates intrusion evaluation, risk assessment, alert generation,
    deduplication, and event persistence.
    """

    def __init__(
        self,
        camera_id: str = "CAM-01",
        db_service: Optional[Any] = None,
        database_path: Optional[str] = None,
        minimum_alert_severity: str = "MEDIUM",
        cooldown_seconds: float = 10.0,
    ):
        self.camera_id = camera_id
        if db_service is not None:
            self.db_service = db_service
        elif database_path is not None:
            self.db_service = DatabaseService(database_path)
        else:
            self.db_service = None

        self.intrusion_engine = IntrusionEngine(camera_id=camera_id)
        self.risk_engine = RiskEngine()
        self.alert_engine = AlertEngine(minimum_severity=minimum_alert_severity)
        self.deduplicator = EventDeduplicator(cooldown_seconds=cooldown_seconds)
        self.summary = EventSummary()

        self._register_camera()

    def _register_camera(self):
        if self.db_service and hasattr(self.db_service, "cameras"):
            try:
                self.db_service.cameras.add_camera(
                    camera_id=self.camera_id,
                    camera_name=f"Camera {self.camera_id}",
                    location="Virtual Sector A"
                )
            except Exception:
                pass

    def process_track(
        self,
        track_id: int,
        object_type: str,
        confidence: float,
        previous_zone: Optional[str],
        current_zone: Optional[str],
        direction: str = "UNKNOWN",
        speed: float = 0.0,
        dwell_time: float = 0.0,
        timestamp: Optional[float] = None,
    ) -> Tuple[Optional[Any], Optional[Any], Optional[Any]]:
        """
        Process object track through pipeline lifecycle.
        Returns (event, risk, alert) tuple.
        """
        if timestamp is None:
            timestamp = time.time()

        # 1. Intrusion evaluation
        event = self.intrusion_engine.evaluate(
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

        if event is None:
            return None, None, None

        # 2. Deduplication check
        if not self.deduplicator.should_create_event(track_id=track_id, current_time=timestamp):
            return None, None, None

        # 3. Risk evaluation
        risk_result = self.risk_engine.evaluate(event)

        # 4. Alert generation
        alert = self.alert_engine.create_alert(event, risk_result)

        # 5. Database persistence
        if self.db_service:
            try:
                if hasattr(self.db_service, "events"):
                    self.db_service.events.save_event(event)
                if hasattr(self.db_service, "risks"):
                    self.db_service.risks.save_risk(event, risk_result)
                if alert and hasattr(self.db_service, "alerts"):
                    self.db_service.alerts.save_alert(alert)
                if hasattr(self.db_service, "logger"):
                    risk_score = risk_result.score if risk_result else 0.0
                    severity = risk_result.severity if risk_result else "UNKNOWN"
                    self.db_service.logger.log(
                        level="WARNING",
                        component="SECURITY_PIPELINE",
                        message=f"{event.event_type} detected for track {event.track_id}; risk={risk_score:.2f}; severity={severity}"
                    )
            except Exception as e:
                print(f"[EventOrchestrator] Persistence warning: {e}")

        # 6. Event summary tracking
        self.summary.add_event(event, risk_result, alert)

        return event, risk_result, alert

    def process(
        self,
        track_id: int,
        object_type: str,
        confidence: float,
        previous_zone: Optional[str],
        current_zone: Optional[str],
        direction: str = "UNKNOWN",
        speed: float = 0.0,
        dwell_time: float = 0.0,
        timestamp: Optional[float] = None,
    ) -> Dict[str, Optional[Any]]:
        """
        Process object track and return a result dictionary.
        """
        evt, rsk, alt = self.process_track(
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
        return {
            "event": evt,
            "risk": rsk,
            "alert": alt,
            "summary": self.summary,
        }

    def reset(self):
        """Reset internal state."""
        self.intrusion_engine.events.clear()
        self.intrusion_engine.active_rules.clear()
        self.alert_engine.alerts.clear()
        self.deduplicator.last_event_time.clear()
        self.summary.reset()

    def close(self):
        if self.db_service and hasattr(self.db_service, "close"):
            self.db_service.close()
