import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "src"))

try:
    from database import Database
    from camera_repository import CameraRepository
    from event_repository import EventRepository
    from risk_repository import RiskRepository
    from alert_repository import AlertRepository
    from system_logger import SystemLogger
    from schema import SCHEMA
except ImportError:
    from src.database.database import Database
    from src.database.camera_repository import CameraRepository
    from src.database.event_repository import EventRepository
    from src.database.risk_repository import RiskRepository
    from src.database.alert_repository import AlertRepository
    from src.database.system_logger import SystemLogger
    from src.database.schema import SCHEMA


class DatabaseService:

    def __init__(
        self,
        database_path: str = "data/database/borderguard.db",
    ):
        self.database = Database(database_path)
        self.cameras = CameraRepository(self.database)
        self.events = EventRepository(self.database)
        self.risks = RiskRepository(self.database)
        self.alerts = AlertRepository(self.database)
        self.logger = SystemLogger(self.database)

    def reset_database(self):
        """
        Clears all data from database tables and re-initializes schema.
        """
        conn = self.database.connect()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF;")
        tables = ["alerts", "risk_assessments", "intrusion_events", "tracks", "system_logs", "cameras", "evaluation_results"]
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
        conn.executescript(SCHEMA)
        cursor.execute("PRAGMA foreign_keys = ON;")
        conn.commit()

    def close(self):
        self.database.close()
