import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "src"))

try:
    from src.database.database_service import DatabaseService
except ImportError:
    try:
        from database_service import DatabaseService
    except ImportError:
        from data.database.database_service import DatabaseService


def reset_database(db_path: str = "data/database/borderguard.db"):
    """
    Utility script to reset the BorderGuard AI database.
    """
    full_path = BASE_DIR / db_path if not Path(db_path).is_absolute() else Path(db_path)
    db_service = DatabaseService(str(full_path))
    db_service.reset_database()
    db_service.close()
    print(f"[Database] Reset utility successfully cleared and re-initialized: {full_path}")


if __name__ == "__main__":
    reset_database()
