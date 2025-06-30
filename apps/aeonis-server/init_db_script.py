
import os
import sys
from aeonis_server.db.database import init_db

# Add the parent directory to the Python path to allow for relative imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialization complete.")
