import uuid
import secrets
from aeonis_server.db.database import SessionLocal, init_db
from aeonis_server.db.models import Project

def create_project(name: str):
    """
    Creates a new project in the database with a securely generated API key.
    """
    db = SessionLocal()
    try:
        # Check if a project with this name already exists
        existing_project = db.query(Project).filter(Project.name == name).first()
        if existing_project:
            print(f"Project '{name}' already exists.")
            print(f"  - Project ID: {existing_project.id}")
            print(f"  - API Key:    {existing_project.api_key}")
            return

        # Create new project
        project = Project(
            id=uuid.uuid4(),
            name=name,
            api_key=secrets.token_urlsafe(32)
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        print(f"Successfully created project '{name}'.")
        print(f"  - Project ID: {project.id}")
        print(f"  - API Key:    {project.api_key}")

    finally:
        db.close()

if __name__ == "__main__":
    # Initialize the database (creates tables if they don't exist)
    init_db()
    
    # Create the 'Invoxa' project
    create_project("Invoxa")
