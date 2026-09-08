from datetime import datetime, timezone


class CameraRepository:

    def __init__(
        self,
        database,
    ):
        self.database = database

    def add_camera(
        self,
        camera_id: str,
        camera_name: str,
        location: str = "",
        status: str = "ACTIVE",
    ):
        connection = self.database.connect()
        timestamp = datetime.now(timezone.utc).isoformat()
        connection.execute(
            """
            INSERT OR REPLACE INTO cameras
            (
                camera_id,
                camera_name,
                location,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                camera_id,
                camera_name,
                location,
                status,
                timestamp,
            ),
        )
        connection.commit()

    def get_camera(
        self,
        camera_id: str,
    ):
        connection = self.database.connect()
        cursor = connection.execute(
            """
            SELECT *
            FROM cameras
            WHERE camera_id = ?
            """,
            (camera_id,),
        )
        return cursor.fetchone()

    def get_all_cameras(self):
        connection = self.database.connect()
        cursor = connection.execute(
            """
            SELECT *
            FROM cameras
            ORDER BY camera_id
            """
        )
        return cursor.fetchall()
