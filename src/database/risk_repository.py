from datetime import datetime, timezone


class RiskRepository:

    def __init__(
        self,
        database,
    ):
        self.database = database

    def save_risk(
        self,
        event,
        risk_result,
    ):
        connection = self.database.connect()
        breakdown = risk_result.breakdown
        timestamp = datetime.now(timezone.utc).isoformat()

        connection.execute(
            """
            INSERT OR REPLACE INTO
            risk_assessments
            (
                event_id,
                risk_score,
                severity,
                zone_contribution,
                object_contribution,
                direction_contribution,
                dwell_contribution,
                confidence_contribution,
                event_contribution,
                created_at
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?
            )
            """,
            (
                event.event_id,
                risk_result.score,
                risk_result.severity,
                breakdown["zone"]["contribution"],
                breakdown["object_type"]["contribution"],
                breakdown["direction"]["contribution"],
                breakdown["dwell_time"]["contribution"],
                breakdown["confidence"]["contribution"],
                breakdown["event_type"]["contribution"],
                timestamp,
            ),
        )
        connection.commit()

    def get_risk_for_event(
        self,
        event_id: str,
    ):
        connection = self.database.connect()
        cursor = connection.execute(
            """
            SELECT *
            FROM risk_assessments
            WHERE event_id = ?
            """,
            (event_id,),
        )
        return cursor.fetchone()
