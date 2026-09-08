from datetime import datetime, timezone


class AlertRepository:

    def __init__(
        self,
        database,
    ):
        self.database = database

    def save_alert(
        self,
        alert,
    ):
        connection = self.database.connect()
        timestamp = datetime.fromtimestamp(
            alert.timestamp,
            timezone.utc,
        ).isoformat()

        connection.execute(
            """
            INSERT OR IGNORE INTO alerts
            (
                alert_id,
                event_id,
                timestamp,
                camera_id,
                track_id,
                object_type,
                message,
                severity,
                risk_score,
                acknowledged
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?
            )
            """,
            (
                alert.alert_id,
                alert.event_id,
                timestamp,
                alert.camera_id,
                alert.track_id,
                alert.object_type,
                alert.message,
                alert.severity,
                alert.risk_score,
                int(alert.acknowledged),
            ),
        )
        connection.commit()

    def get_active_alerts(self):
        connection = self.database.connect()
        cursor = connection.execute(
            """
            SELECT *
            FROM alerts
            WHERE acknowledged = 0
            ORDER BY timestamp DESC
            """
        )
        return cursor.fetchall()

    def acknowledge_alert(
        self,
        alert_id: str,
    ):
        connection = self.database.connect()
        connection.execute(
            """
            UPDATE alerts
            SET acknowledged = 1
            WHERE alert_id = ?
            """,
            (alert_id,),
        )
        connection.commit()
