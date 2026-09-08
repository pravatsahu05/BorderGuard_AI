import sqlite3
from pathlib import Path


class Database:
    """
    SQLite database manager for BorderGuard AI.
    """

    def __init__(
        self,
        database_path: str = "data/database/borderguard.db",
    ):
        self.database_path = Path(database_path)

        # Make sure the database directory exists.
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = None

    def connect(self):
        """
        Open a connection to the SQLite database.
        """
        if self.connection is None:
            self.connection = sqlite3.connect(self.database_path)
            # Allows rows to be accessed by column name.
            self.connection.row_factory = sqlite3.Row

        return self.connection

    def close(self):
        """
        Close the database connection.
        """
        if self.connection is not None:
            self.connection.close()
            self.connection = None
