"""
Database management module for BorderGuard AI.
"""
from src.database.database import Database
from src.database.schema import SCHEMA
from src.database.database_service import DatabaseService
from src.database.camera_repository import CameraRepository
from src.database.event_repository import EventRepository
from src.database.risk_repository import RiskRepository
from src.database.alert_repository import AlertRepository
from src.database.system_logger import SystemLogger

__all__ = [
    "Database",
    "SCHEMA",
    "DatabaseService",
    "CameraRepository",
    "EventRepository",
    "RiskRepository",
    "AlertRepository",
    "SystemLogger",
]
