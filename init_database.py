from app.database import init_db
from app.core.utils import logger

def main():
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    main() 