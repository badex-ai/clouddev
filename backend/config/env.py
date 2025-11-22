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

def build_url(host: str, port: int, db: int, password: str = "", use_ssl: bool = False) -> str:
    """Build Redis URL from components"""
    protocol = "rediss" if use_ssl else "redis"
    if password:
        return f"{protocol}://:{password}@{host}:{port}/{db}"
    return f"{protocol}://{host}:{port}/{db}"


def get_config() -> dict:
    """Get configuration based on environment"""
    environment = os.getenv("ENVIRONMENT")
    
    # Log environment for debugging
    print(f"[CONFIG] Loading configuration for environment: {environment}")

    # If NOT localdev, read secrets from /etc/secrets/
    if environment != "dev":
        auth0_client_secret = read_secret_file("/etc/secrets/AUTH0_CLIENT_SECRET")
        auth0_m2m_client_secret = read_secret_file(
            "/etc/secrets/AUTH0_M2M_CLIENT_SECRET"
        )
        db_password = read_secret_file("/etc/secrets/DB_PASSWORD")
        brevo_api_key = read_secret_file("/etc/secrets/BREVO_API_KEY")
        redis_password = read_secret_file("/etc/secrets/REDIS_PASSWORD")
        celery_broker_password = read_secret_file("/etc/secrets/CELERY_BROKER_PASSWORD")
        celery_result_password = read_secret_file("/etc/secrets/CELERY_RESULT_PASSWORD")
    else:
        # In localdev, use environment variables
        auth0_client_secret = os.getenv("AUTH0_CLIENT_SECRET")
        auth0_m2m_client_secret = os.getenv("AUTH0_M2M_CLIENT_SECRET")
        db_password = os.getenv("DB_PASSWORD")
        brevo_api_key = os.getenv("BREVO_API_KEY")
        redis_password = os.getenv("REDIS_PASSWORD", "")
        celery_broker_password = os.getenv("CELERY_BROKER_PASSWORD", "")
        celery_result_password = os.getenv("CELERY_RESULT_PASSWORD", "")
    # Non-sensitive configuration - always from environment variables
    # STRICT: Use os.environ to fail fast if missing
    redis_host = os.environ["REDIS_HOST"]
    redis_port = int(os.environ["REDIS_PORT"])
    redis_db = int(os.environ["REDIS_DB"])
    redis_use_ssl = os.getenv("REDIS_USE_SSL", "false").lower() == "true"
    
    celery_broker_host = os.environ["CELERY_BROKER_HOST"]
    celery_broker_port = int(os.environ["CELERY_BROKER_PORT"])
    celery_broker_db = int(os.environ["CELERY_BROKER_DB"])
    celery_broker_use_ssl = os.getenv("CELERY_BROKER_USE_SSL", "false").lower() == "true"
    
    celery_result_host = os.environ["CELERY_RESULT_HOST"]
    celery_result_port = int(os.environ["CELERY_RESULT_PORT"])
    celery_result_db = int(os.environ["CELERY_RESULT_DB"])
    celery_result_use_ssl = os.getenv("CELERY_RESULT_USE_SSL", "false").lower() == "true"
    sender_email = os.environ["BREVO_SENDER_EMAIL"]

    # Build URLs using non-sensitive config + sensitive passwords
    redis_url = build_url(redis_host, redis_port, redis_db, redis_password, redis_use_ssl)
    celery_broker_url = build_url(
        celery_broker_host, celery_broker_port, celery_broker_db, 
        celery_broker_password, celery_broker_use_ssl
    )
    celery_result_backend = build_url(
        celery_result_host, celery_result_port, celery_result_db, 
        celery_result_password, celery_result_use_ssl
    )

    # Log configuration (without sensitive data)
    print(f"[CONFIG] Redis URL: redis://{redis_host}:{redis_port}/{redis_db}")
    print(f"[CONFIG] Celery Broker URL: redis://{celery_broker_host}:{celery_broker_port}/{celery_broker_db}")
    print(f"[CONFIG] Celery Result Backend: redis://{celery_result_host}:{celery_result_port}/{celery_result_db}")

    

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


        "redis_url": redis_url,
        "celery_broker_url": celery_broker_url,
        "celery_result_backend": celery_result_backend,
        "sender_email": sender_email

        
    }
