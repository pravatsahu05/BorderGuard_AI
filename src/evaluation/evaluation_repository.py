import sqlite3
from pathlib import Path


class EvaluationRepository:

    def __init__(
        self,
        database_path=("data/database/" "borderguard.db"),
    ):

        self.database_path = Path(database_path)

    def _connect(self):
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.database_path)
        conn.execute(
            """
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
        )
        conn.commit()
        return conn


    def save_result(
        self,
        model_name,
        dataset_name,
        result,
        map50=None,
        map5095=None,
        fps=None,
        latency_ms=None,
    ):

        connection = self._connect()

        connection.execute(
            """
            INSERT INTO
            evaluation_results (

                model_name,
                dataset_name,
                precision,
                recall,
                f1_score,
                mean_iou,
                map50,
                map5095,
                fps,
                latency_ms,
                created_at

            )

            VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, datetime('now')
            )
            """,
            (
                model_name,
                dataset_name,
                result.precision,
                result.recall,
                result.f1_score,
                result.mean_iou,
                map50,
                map5095,
                fps,
                latency_ms,
            ),
        )

        connection.commit()

        connection.close()

    def get_results(
        self,
    ):

        connection = self._connect()

        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT *
            FROM evaluation_results
            ORDER BY created_at DESC
            """
        ).fetchall()

        connection.close()

        return [dict(row) for row in rows]
