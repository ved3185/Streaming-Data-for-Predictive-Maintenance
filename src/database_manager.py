import os
import pandas as pd
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


class DatabaseManager:
    def __init__(self):
        # Find the main PredictiveMaintenance project folder
        project_root = Path(__file__).resolve().parents[1]

        # Find the private .env file
        env_path = project_root / ".env"

        # Load values stored inside .env
        load_dotenv(env_path)

        # Read the Neon connection string
        self.database_url = os.getenv("DATABASE_URL")

        if not self.database_url:
            raise ValueError(
                "DATABASE_URL was not found. Check your .env file."
            )

        # Tell SQLAlchemy to use psycopg version 3
        url = make_url(self.database_url).set(
            drivername="postgresql+psycopg"
        )

        # Create the connection engine
        self.engine = create_engine(
            url,
            pool_pre_ping=True
        )

    def test_connection(self):
        with self.engine.connect() as connection:
            result = connection.execute(
                text("SELECT version();")
            )

            return result.scalar()

    def create_training_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS training_data (
            id SERIAL PRIMARY KEY,
            sampled_at TIMESTAMPTZ NOT NULL,
            trait TEXT,
            axis_1 DOUBLE PRECISION,
            axis_2 DOUBLE PRECISION,
            axis_3 DOUBLE PRECISION,
            axis_4 DOUBLE PRECISION,
            axis_5 DOUBLE PRECISION,
            axis_6 DOUBLE PRECISION,
            axis_7 DOUBLE PRECISION,
            axis_8 DOUBLE PRECISION
        );
        """

        with self.engine.begin() as connection:
            connection.execute(text(create_table_sql))

    def count_training_rows(self):
        with self.engine.connect() as connection:
            result = connection.execute(
                text("SELECT COUNT(*) FROM training_data;")
            )

            return result.scalar()


    def upload_training_data(self, dataframe):
        existing_rows = self.count_training_rows()

        if existing_rows > 0:
            print(
                f"Training table already contains "
                f"{existing_rows} rows. Upload skipped."
            )
            return

        upload_df = dataframe[
            [
                "Time",
                "Trait",
                "Axis #1",
                "Axis #2",
                "Axis #3",
                "Axis #4",
                "Axis #5",
                "Axis #6",
                "Axis #7",
                "Axis #8",
            ]
        ].copy()

        upload_df = upload_df.rename(
            columns={
                "Time": "sampled_at",
                "Trait": "trait",
                "Axis #1": "axis_1",
                "Axis #2": "axis_2",
                "Axis #3": "axis_3",
                "Axis #4": "axis_4",
                "Axis #5": "axis_5",
                "Axis #6": "axis_6",
                "Axis #7": "axis_7",
                "Axis #8": "axis_8",
            }
        )

        upload_df["sampled_at"] = pd.to_datetime(
            upload_df["sampled_at"],
            utc=True
        )

        upload_df.to_sql(
            "training_data",
            self.engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )

        print(
            f"{len(upload_df)} training rows uploaded "
            f"successfully to Neon."
        )

    def fetch_training_data(self):
        query = """
        SELECT
            id,
            sampled_at,
            trait,
            axis_1,
            axis_2,
            axis_3,
            axis_4,
            axis_5,
            axis_6,
            axis_7,
            axis_8
        FROM training_data
        ORDER BY sampled_at;
        """

        with self.engine.connect() as connection:
            database_df = pd.read_sql(
                text(query),
                connection
            )

        return database_df

    def create_streaming_table(self):
        column_definitions = [
            "id SERIAL PRIMARY KEY",
            "sampled_at TIMESTAMPTZ NOT NULL",
            "elapsed_seconds DOUBLE PRECISION NOT NULL"
        ]

        for axis_number in range(1, 9):
            column_definitions.extend([
                f"axis_{axis_number} DOUBLE PRECISION",
                f"axis_{axis_number}_normalized DOUBLE PRECISION",
                f"axis_{axis_number}_standardized DOUBLE PRECISION"
            ])

        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS streaming_data (
            {", ".join(column_definitions)}
        );
        """

        with self.engine.begin() as connection:
            connection.execute(text(create_table_sql))


    def clear_streaming_table(self):
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    "TRUNCATE TABLE streaming_data "
                    "RESTART IDENTITY;"
                )
            )


    def insert_streaming_row(self, row):
        column_names = [
            "sampled_at",
            "elapsed_seconds"
        ]

        for axis_number in range(1, 9):
            column_names.extend([
                f"axis_{axis_number}",
                f"axis_{axis_number}_normalized",
                f"axis_{axis_number}_standardized"
            ])

        placeholders = [
            f":{column}"
            for column in column_names
        ]

        insert_sql = f"""
        INSERT INTO streaming_data (
            {", ".join(column_names)}
        )
        VALUES (
            {", ".join(placeholders)}
        );
        """

        values = {}

        for column in column_names:
            value = row[column]

            if column == "sampled_at":
                value = pd.to_datetime(
                    value,
                    utc=True
                ).to_pydatetime()

            elif column != "sampled_at":
                value = float(value)

            values[column] = value

        with self.engine.begin() as connection:
            connection.execute(
                text(insert_sql),
                values
            )


    def count_streaming_rows(self):
        with self.engine.connect() as connection:
            result = connection.execute(
                text(
                    "SELECT COUNT(*) FROM streaming_data;"
                )
            )

            return result.scalar()