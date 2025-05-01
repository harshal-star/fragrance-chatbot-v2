import sqlite3
import os
from datetime import datetime

def inspect_table(db_path, table_name):
    """
    Inspect the contents of a specific table in the database.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Get all rows
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        
        print(f"\n=== Contents of {table_name} table ===")
        print(f"Number of rows: {len(rows)}")
        
        if rows:
            print("\nColumns:", ", ".join(columns))
            print("\nRows:")
            for row in rows:
                print("-" * 80)
                for col, val in zip(columns, row):
                    print(f"{col}: {val}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Error inspecting table {table_name}: {e}")

def inspect_database(db_path):
    """
    Inspect all tables in the database.
    """
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        conn.close()
        
        # Inspect each table
        for (table_name,) in tables:
            inspect_table(db_path, table_name)
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    print("Inspecting fragrance_chatbot.db...")
    inspect_database("fragrance_chatbot.db") 