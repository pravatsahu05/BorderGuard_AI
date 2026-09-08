from datetime import datetime, timezone


class EventRepository:

    def __init__(
        self,
        database,
    ):
        self.database = database

    def save_event(
        self,
        event,
    ):
        connection = self.database.connect()
        timestamp = datetime.fromtimestamp(
            event.timestamp,
            timezone.utc,
        ).isoformat()

        connection.execute(
            """
            INSERT OR IGNORE INTO intrusion_events
            (
                event_id,
                timestamp,
                camera_id,
                track_id,
                object_type,
                confidence,
                previous_zone,
                current_zone,
                direction,
                speed,
                event_type,
                dwell_time,
                severity
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?
            )
            """,
            (
                event.event_id,
                timestamp,
                event.camera_id,
                event.track_id,
                event.object_type,
                event.confidence,
                event.previous_zone,
                event.current_zone,
                event.direction,
                event.speed,
                event.event_type,
                event.dwell_time,
                event.severity,
            ),
        )
        connection.commit()

    def get_event(
        self,
        event_id: str,
    ):
        connection = self.database.connect()
        cursor = connection.execute(
            """
            SELECT *
            FROM intrusion_events
            WHERE event_id = ?
            """,
            (event_id,),
        )
        return cursor.fetchone()

    def get_recent_events(
        self,
        limit: int = 50,
    ):
        connection = self.database.connect()
        cursor = connection.execute(
            """
            SELECT *
            FROM intrusion_events
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cursor.fetchall()

    def count_events(self):
        connection = self.database.connect()
        cursor = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM intrusion_events
            """
        )
        row = cursor.fetchone()
        return row["count"]
