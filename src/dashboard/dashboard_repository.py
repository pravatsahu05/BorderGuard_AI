import sqlite3
from pathlib import Path


class DashboardRepository:
    """
    Read-only database access layer for the
    BorderGuard AI dashboard.
    """

    def __init__(
        self,
        database_path="data/database/borderguard.db",
    ):

        self.database_path = Path(database_path)

    # ========================================================
    # CONNECTION
    # ========================================================

    def _connect(self):

        return sqlite3.connect(self.database_path)

    # ========================================================
    # EVENTS
    # ========================================================

    def get_events(
        self,
        limit=100,
    ):
        """
        Return the latest intrusion events.
        """

        connection = self._connect()

        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT *
            FROM intrusion_events
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        connection.close()

        return [dict(row) for row in rows]

    # ========================================================
    # TOTAL EVENTS
    # ========================================================

    def get_total_events(self):

        connection = self._connect()

        result = connection.execute(
            """
            SELECT COUNT(*)
            FROM intrusion_events
            """
        ).fetchone()

        connection.close()

        return result[0]

    # ========================================================
    # RISK DISTRIBUTION
    # ========================================================

    def get_risk_distribution(self):

        connection = self._connect()

        rows = connection.execute(
            """
            SELECT
                severity,
                COUNT(*) AS count
            FROM risk_assessments
            GROUP BY severity
            """
        ).fetchall()

        connection.close()

        return {row[0]: row[1] for row in rows}

    # ========================================================
    # ACTIVE ALERTS
    # ========================================================

    def get_active_alert_count(self):

        connection = self._connect()

        result = connection.execute(
            """
            SELECT COUNT(*)
            FROM alerts
            WHERE status = 'ACTIVE'
            """
        ).fetchone()

        connection.close()

        return result[0]

    # ========================================================
    # CAMERA COUNT
    # ========================================================

    def get_camera_count(self):

        connection = self._connect()

        result = connection.execute(
            """
            SELECT COUNT(*)
            FROM cameras
            """
        ).fetchone()

        connection.close()

        return result[0]

    # ========================================================
    # ALERTS
    # ========================================================

    def get_alerts(
        self,
        limit=50,
    ):

        connection = self._connect()

        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT *
            FROM alerts
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        connection.close()

        return [dict(row) for row in rows]

    # ========================================================
    # FILTERED EVENTS
    # ========================================================

    def get_events_filtered(
        self,
        severity=None,
        zone=None,
        object_type=None,
        limit=100,
    ):
        """
        Retrieve events using optional filters.
        """

        connection = self._connect()

        connection.row_factory = sqlite3.Row

        query = """
            SELECT *
            FROM intrusion_events
            WHERE 1 = 1
        """

        parameters = []

        # ----------------------------------------------------
        # Severity
        # ----------------------------------------------------

        if severity:

            query += """
                AND severity = ?
            """

            parameters.append(severity)

        # ----------------------------------------------------
        # Zone
        # ----------------------------------------------------

        if zone:

            query += """
                AND current_zone = ?
            """

            parameters.append(zone)

        # ----------------------------------------------------
        # Object type
        # ----------------------------------------------------

        if object_type:

            query += """
                AND object_type = ?
            """

            parameters.append(object_type)

        # ----------------------------------------------------
        # Ordering / limit
        # ----------------------------------------------------

        query += """
            ORDER BY timestamp DESC
            LIMIT ?
        """

        parameters.append(limit)

        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

        connection.close()

        return [dict(row) for row in rows]

    # ========================================================
    # DISTINCT FILTER VALUES
    # ========================================================

    def get_distinct_values(
        self,
        column,
    ):
        """
        Return distinct values from an approved
        database column.

        A whitelist is used because SQL identifiers
        cannot safely be parameterized using ?.
        """

        allowed_columns = {
            "severity",
            "current_zone",
            "object_type",
            "event_type",
        }

        if column not in allowed_columns:

            raise ValueError(f"Invalid column: {column}")

        connection = self._connect()

        rows = connection.execute(
            f"""
            SELECT DISTINCT {column}
            FROM intrusion_events
            WHERE {column} IS NOT NULL
            ORDER BY {column}
            """
        ).fetchall()

        connection.close()

        return [row[0] for row in rows]

    # ========================================================
    # EVENT TIMELINE
    # ========================================================

    def get_event_timeline(self) -> list:

        connection = self._connect()

        rows = connection.execute(
            """
            SELECT
                timestamp,
                COUNT(*) AS event_count
            FROM intrusion_events
            GROUP BY timestamp
            ORDER BY timestamp
            """
        ).fetchall()

        connection.close()

        return [
            {
                "timestamp": row[0],
                "event_count": row[1],
            }
            for row in rows
        ]

    # ========================================================
    # ZONE DISTRIBUTION
    # ========================================================

    def get_zone_distribution(self):

        connection = self._connect()

        rows = connection.execute(
            """
            SELECT
                current_zone,
                COUNT(*) AS count
            FROM intrusion_events
            GROUP BY current_zone
            ORDER BY count DESC
            """
        ).fetchall()

        connection.close()

        return {row[0]: row[1] for row in rows}

    # ========================================================
    # EVENT TYPE DISTRIBUTION
    # ========================================================

    def get_event_type_distribution(self):

        connection = self._connect()

        rows = connection.execute(
            """
            SELECT
                event_type,
                COUNT(*) AS count
            FROM intrusion_events
            GROUP BY event_type
            ORDER BY count DESC
            """
        ).fetchall()

        connection.close()

        return {row[0]: row[1] for row in rows}
