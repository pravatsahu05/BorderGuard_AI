import time
import uuid

try:
    from intrusion.event import IntrusionEvent
except (ImportError, ValueError):
    try:
        from src.intrusion.event import IntrusionEvent
    except ImportError:
        from event import IntrusionEvent


try:
    from intrusion.config import INTRUSION_CONFIG
except (ImportError, ValueError):
    try:
        from src.intrusion.config import INTRUSION_CONFIG
    except ImportError:
        from config import INTRUSION_CONFIG




class IntrusionEngine:
    """
    Configurable security rule engine.

    Supported rules:
        - Restricted zone entry
        - Dwell time violation
        - Direction violation
    """

    def __init__(
        self,
        camera_id: str = "CAM-01",
    ):

        self.camera_id = camera_id

        self.events = []

        # Used to avoid repeated alerts.
        self.active_rules = set()

    def _create_event(
        self,
        track_id,
        object_type,
        confidence,
        previous_zone,
        current_zone,
        direction,
        speed,
        dwell_time,
        event_type,
        severity,
        timestamp,
    ):

        event_id = f"EVT-" f"{uuid.uuid4().hex[:8].upper()}"

        event = IntrusionEvent(
            event_id=event_id,
            timestamp=timestamp,
            camera_id=self.camera_id,
            track_id=track_id,
            object_type=object_type,
            confidence=confidence,
            previous_zone=previous_zone,
            current_zone=current_zone,
            direction=direction,
            speed=speed,
            event_type=event_type,
            dwell_time=dwell_time,
            severity=severity,
        )

        self.events.append(event)

        return event

    def evaluate(
        self,
        track_id: int,
        object_type: str,
        confidence: float,
        previous_zone,
        current_zone,
        direction: str,
        speed: float,
        dwell_time: float,
        timestamp: float | None = None,
    ):

        if timestamp is None:
            timestamp = time.time()

        # ====================================================
        # RULE 1 — RESTRICTED ZONE ENTRY
        # ====================================================

        restricted_enabled = INTRUSION_CONFIG["restricted_zone_entry"]["enabled"]

        entering_restricted = (
            current_zone == "RESTRICTED"
            and previous_zone is not None
            and previous_zone != "RESTRICTED"
        )

        if restricted_enabled and entering_restricted:

            rule_key = (
                track_id,
                "RESTRICTED_ZONE_ENTRY",
                previous_zone,
                current_zone,
            )

            if rule_key not in self.active_rules:

                self.active_rules.add(rule_key)

                return self._create_event(
                    track_id,
                    object_type,
                    confidence,
                    previous_zone,
                    current_zone,
                    direction,
                    speed,
                    dwell_time,
                    "RESTRICTED_ZONE_ENTRY",
                    "HIGH",
                    timestamp,
                )

        # ====================================================
        # RULE 2 — DWELL TIME
        # ====================================================

        dwell_config = INTRUSION_CONFIG["dwell_time_violation"]

        if dwell_config["enabled"]:

            if current_zone == "RESTRICTED":

                threshold = dwell_config["restricted_seconds"]

                if dwell_time >= threshold:

                    rule_key = (
                        track_id,
                        "RESTRICTED_DWELL",
                    )

                    if rule_key not in self.active_rules:

                        self.active_rules.add(rule_key)

                        return self._create_event(
                            track_id,
                            object_type,
                            confidence,
                            previous_zone,
                            current_zone,
                            direction,
                            speed,
                            dwell_time,
                            "RESTRICTED_DWELL_VIOLATION",
                            "CRITICAL",
                            timestamp,
                        )

        # ====================================================
        # RULE 3 — DIRECTION
        # ====================================================

        direction_config = INTRUSION_CONFIG["direction_violation"]

        if direction_config["enabled"]:

            allowed_direction = direction_config["allowed_direction"]

            if (
                current_zone == "WARNING"
                and direction != allowed_direction
                and direction != "UNKNOWN"
                and direction != "STATIONARY"
            ):

                rule_key = (
                    track_id,
                    "DIRECTION_VIOLATION",
                    direction,
                )

                if rule_key not in self.active_rules:

                    self.active_rules.add(rule_key)

                    return self._create_event(
                        track_id,
                        object_type,
                        confidence,
                        previous_zone,
                        current_zone,
                        direction,
                        speed,
                        dwell_time,
                        "DIRECTION_VIOLATION",
                        "MEDIUM",
                        timestamp,
                    )

        return None
