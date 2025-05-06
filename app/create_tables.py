from app.core.database import engine
from app.models.models import Base

print("Creating all tables in the database...")
Base.metadata.create_all(bind=engine)
print("Done.")