import os
from pathlib import Path
from functools import lru_cache
from dotenv import load_dotenv
import base64


load_dotenv()

def read_secret_file(file_path: str) -> str:
    try:
        path = Path(file_path)
        if path.exists():
            content = path.read_text().strip()
            # Try to decode if it's base64
            try:
                decoded = base64.b64decode(content).decode("utf-8")
                return decoded
            except Exception:
                # If decoding fails, return as-is
                return content
    except Exception as e:
        print(f"Error reading secret file {file_path}: {e}")
    return ""

@lru_cache()
def get_config() -> dict:
    """Get configuration based on environment"""
    environment = os.getenv("ENVIRONMENT")
    
    # If NOT localdev, read secrets from /etc/secrets/
    if environment != "dev":
        auth0_client_secret = read_secret_file("/etc/secrets/AUTH0_CLIENT_SECRET")
        auth0_m2m_client_secret = read_secret_file("/etc/secrets/AUTH0_M2M_CLIENT_SECRET")
        db_password = read_secret_file("/etc/secrets/DB_PASSWORD")
        brevo_api_key = read_secret_file("/etc/secrets/BREVO_API_KEY")
    else:
        # In localdev, use environment variables
        auth0_client_secret = os.getenv("AUTH0_CLIENT_SECRET")
        auth0_m2m_client_secret = os.getenv("AUTH0_M2M_CLIENT_SECRET")
        db_password = os.getenv("DB_PASSWORD")
        brevo_api_key = os.getenv("BREVO_API_KEY")
    
    # Non-secret config (from environment variables in all environments)
    return {
        # Auth0 settings
        "auth0_domain": os.getenv("AUTH0_DOMAIN"),
        "auth0_client_id": os.getenv("AUTH0_CLIENT_ID"),
        "auth0_client_secret": auth0_client_secret,
        "auth0_api_audience": os.getenv("AUTH0_API_AUDIENCE"),
        "auth0_m2m_client_id": os.getenv("AUTH0_M2M_CLIENT_ID"),
        "brevo_api_key": brevo_api_key,
        "auth0_m2m_client_secret": auth0_m2m_client_secret,
        
        # Database settings
        "db_host": os.getenv("DB_HOST"),
        "db_port": os.getenv("DB_PORT"),
        "db_name": os.getenv("DB_NAME"),
        "db_user": os.getenv("DB_USER"),
        "db_password": db_password,
        
        # App settings
        "environment": environment,
        "debug": os.getenv("DEBUG", "false").lower() == "true",
    }


