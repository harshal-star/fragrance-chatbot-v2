from sqlalchemy import create_engine, inspect
import os
from datetime import datetime

# Function to inspect a specific table (fetches all rows)
def inspect_table(engine, table_name):
    from sqlalchemy import text
    with engine.connect() as conn:
        # Get column names
        result = conn.execute(text(f'SELECT * FROM "{table_name}" LIMIT 0'))
        columns = result.keys()
        # Get all rows
        rows = conn.execute(text(f'SELECT * FROM "{table_name}"')).fetchall()
        print(f"\n=== Contents of {table_name} table ===")
        print(f"Number of rows: {len(rows)}")
        if rows:
            print("\nColumns:", ", ".join(columns))
            print("\nRows:")
            for row in rows:
                print("-" * 80)
                for col, val in zip(columns, row):
                    print(f"{col}: {val}")

# Function to inspect all tables in the database
def inspect_database(db_url):
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if not tables:
        print(f"No tables found in {db_url}.")
        return
    for table_name in tables:
        inspect_table(engine, table_name)

if __name__ == "__main__":
    db_url = os.getenv("DATABASE_URL", "sqlite:///./fragrance_chatbot.db")
    print(f"Inspecting {db_url}...")
    inspect_database(db_url) 