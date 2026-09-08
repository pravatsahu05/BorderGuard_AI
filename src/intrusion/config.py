INTRUSION_CONFIG = {
    "restricted_zone_entry": {
        "enabled": True,
    },
    "dwell_time_violation": {
        "enabled": True,
        "restricted_seconds": 10.0,
        "warning_seconds": 20.0,
    },
    "direction_violation": {
        "enabled": True,
        "allowed_direction": "DOWN",
    },
}
