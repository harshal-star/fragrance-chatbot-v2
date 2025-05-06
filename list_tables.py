from sqlalchemy import create_engine, inspect
import os

def list_tables(db_url):
    """
    Connect to a SQLite database and list all tables in it.
    
    Args:
        db_url (str): URL to the database
    
    Returns:
        list: List of table names
    """
    # Check if the file exists
    if not os.path.exists(db_url):
        print(f"Error: Database file '{db_url}' not found.")
        return []
    
    try:
        # Connect to the database
        engine = create_engine(db_url)
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        # Print results
        if table_names:
            print(f"\nFound {len(table_names)} tables in {db_url}:")
            for i, table in enumerate(table_names, 1):
                print(f"{i}. {table}")
        else:
            print(f"\nNo tables found in {db_url}.")
            
        return table_names
        
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    # Example usage: set your database URL here
    db_url = os.getenv("DATABASE_URL", "sqlite:///./fragrance_chatbot.db")
    list_tables(db_url) 