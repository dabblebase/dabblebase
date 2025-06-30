"""Load environment variables from a .env file"""

import os
import dotenv
from pydantic import BaseModel


# Create a pydantic model to validate environment variables
class EnvModel(BaseModel):
    """Pydantic model to validate the environment variables."""

    MODE: str
    ADMIN_DB_USER: str
    ADMIN_DB_PASSWORD: str
    ADMIN_DB_HOST: str
    ADMIN_DB_PORT: str
    ADMIN_DB_DATABASE: str
    CONTENT_DB_USER: str
    CONTENT_DB_PASSWORD: str
    CONTENT_DB_HOST: str
    CONTENT_DB_PORT: str
    CONTENT_DB_DATABASE: str
    JWT_SECRET: str


# Load envirnment variables from .env file upon module start.
dotenv.load_dotenv(f"{os.path.dirname(__file__)}/.env", verbose=True)

# Export the environment variables as a pydantic model instance for
# easy access and validation.
env = EnvModel(
    MODE=os.getenv("MODE"),
    ADMIN_DB_USER=os.getenv("ADMIN_DB_USER"),
    ADMIN_DB_PASSWORD=os.getenv("ADMIN_DB_PASSWORD"),
    ADMIN_DB_HOST=os.getenv("ADMIN_DB_HOST"),
    ADMIN_DB_PORT=os.getenv("ADMIN_DB_PORT"),
    ADMIN_DB_DATABASE=os.getenv("ADMIN_DB_DATABASE"),
    CONTENT_DB_USER=os.getenv("CONTENT_DB_USER"),
    CONTENT_DB_PASSWORD=os.getenv("CONTENT_DB_PASSWORD"),
    CONTENT_DB_HOST=os.getenv("CONTENT_DB_HOST"),
    CONTENT_DB_PORT=os.getenv("CONTENT_DB_PORT"),
    CONTENT_DB_DATABASE=os.getenv("CONTENT_DB_DATABASE"),
    JWT_SECRET=os.getenv("JWT_SECRET"),
)


def in_production() -> bool:
    """Returns `true` if the app is running in production (based on the env file)."""
    return env.MODE == "production"
