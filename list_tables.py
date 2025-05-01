import sqlite3
import os

def list_tables(db_path):
    """
    Connect to a SQLite database and list all tables in it.
    
    Args:
        db_path (str): Path to the SQLite database file
    
    Returns:
        list: List of table names
    """
    # Check if the file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found.")
        return []
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query to get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Close connection
        conn.close()
        
        # Extract table names from results
        table_names = [table[0] for table in tables]
        
        # Print results
        if table_names:
            print(f"\nFound {len(table_names)} tables in {db_path}:")
            for i, table in enumerate(table_names, 1):
                print(f"{i}. {table}")
        else:
            print(f"\nNo tables found in {db_path}.")
            
        return table_names
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []

if __name__ == "__main__":
    # Check both database files
    print("Checking databases...")
    list_tables("fragrance_chatbot.db")
    list_tables("sessions.db") 