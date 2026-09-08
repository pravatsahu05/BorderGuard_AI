SCHEMA = """

PRAGMA foreign_keys = ON;


-- ==========================================================
-- CAMERAS
-- ==========================================================

CREATE TABLE IF NOT EXISTS cameras (

    camera_id TEXT PRIMARY KEY,

    camera_name TEXT NOT NULL,

    location TEXT,

    status TEXT DEFAULT 'ACTIVE',

    created_at TEXT NOT NULL
);


-- ==========================================================
-- TRACKS
-- ==========================================================

CREATE TABLE IF NOT EXISTS tracks (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    camera_id TEXT NOT NULL,

    track_id INTEGER NOT NULL,

    object_type TEXT NOT NULL,

    first_seen TEXT NOT NULL,

    last_seen TEXT NOT NULL,

    FOREIGN KEY (
        camera_id
    )
    REFERENCES cameras(camera_id)
);


-- ==========================================================
-- INTRUSION EVENTS
-- ==========================================================

CREATE TABLE IF NOT EXISTS intrusion_events (

    event_id TEXT PRIMARY KEY,

    timestamp TEXT NOT NULL,

    camera_id TEXT NOT NULL,

    track_id INTEGER NOT NULL,

    object_type TEXT NOT NULL,

    confidence REAL NOT NULL,

    previous_zone TEXT,

    current_zone TEXT,

    direction TEXT,

    speed REAL,

    event_type TEXT NOT NULL,

    dwell_time REAL,

    severity TEXT,

    FOREIGN KEY (
        camera_id
    )
    REFERENCES cameras(camera_id)
);


-- ==========================================================
-- RISK ASSESSMENTS
-- ==========================================================

CREATE TABLE IF NOT EXISTS risk_assessments (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    event_id TEXT NOT NULL UNIQUE,

    risk_score REAL NOT NULL,

    severity TEXT NOT NULL,

    zone_contribution REAL,

    object_contribution REAL,

    direction_contribution REAL,

    dwell_contribution REAL,

    confidence_contribution REAL,

    event_contribution REAL,

    created_at TEXT NOT NULL,

    FOREIGN KEY (
        event_id
    )
    REFERENCES intrusion_events(event_id)
);


-- ==========================================================
-- ALERTS
-- ==========================================================

CREATE TABLE IF NOT EXISTS alerts (

    alert_id TEXT PRIMARY KEY,

    event_id TEXT NOT NULL,

    timestamp TEXT NOT NULL,

    camera_id TEXT NOT NULL,

    track_id INTEGER NOT NULL,

    object_type TEXT NOT NULL,

    message TEXT NOT NULL,

    severity TEXT NOT NULL,

    risk_score REAL NOT NULL,

    acknowledged INTEGER DEFAULT 0,

    FOREIGN KEY (
        event_id
    )
    REFERENCES intrusion_events(event_id)
);


-- ==========================================================
-- SYSTEM LOGS
-- ==========================================================

CREATE TABLE IF NOT EXISTS system_logs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    timestamp TEXT NOT NULL,

    level TEXT NOT NULL,

    component TEXT NOT NULL,

    message TEXT NOT NULL
);


-- ==========================================================
-- EVALUATION RESULTS
-- ==========================================================

CREATE TABLE IF NOT EXISTS evaluation_results (

    evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,

    model_name TEXT NOT NULL,

    dataset_name TEXT,

    precision REAL,

    recall REAL,

    f1_score REAL,

    mean_iou REAL,

    map50 REAL,

    map5095 REAL,

    fps REAL,

    latency_ms REAL,

    created_at TEXT NOT NULL
);


"""

