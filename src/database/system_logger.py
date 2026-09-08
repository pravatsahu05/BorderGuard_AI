from datetime import datetime, timezone


class SystemLogger:

    def __init__(
        self,
        database,
    ):
        self.database = database

    def log(
        self,
        level: str,
        component: str,
        message: str,
    ):
        connection = self.database.connect()
        timestamp = datetime.now(timezone.utc).isoformat()
        connection.execute(
            """
            INSERT INTO system_logs
            (
                timestamp,
                level,
                component,
                message
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                timestamp,
                level,
                component,
                message,
            ),
        )
        connection.commit()
