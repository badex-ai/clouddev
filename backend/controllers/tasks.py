from config.celery import celery_app
from utils.utils import send_email
from utils.email_templates import FAMILY_MEMBER_WELCOME_EMAIL, VERIFICATION_EMAIL
import httpx
from structlog import get_logger

logger = get_logger()


@celery_app.task(bind=True, max_retries=3)
def send_welcome_email_task(self, email: str, name: str, password_reset_url: str, admin_name: str):
    try:
        formatted_email = FAMILY_MEMBER_WELCOME_EMAIL.format(
            name=name,
            admin_name=admin_name,
            password_reset_url=password_reset_url
        )
        
        email_req = type('obj', (object,), {'email': email})()
        send_email(email_req, formatted_email)
        
        logger.info("welcome_email_sent", email=email)
        return {"status": "success", "email": email}
        
    except Exception as e:
        logger.warning("welcome_email_failed", email=email, error=str(e))
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def send_password_reset_task(self, user_id: str, m2m_token: str, auth0_domain: str):

    try:
        ticket_url = f"https://{auth0_domain}/api/v2/tickets/password-change"
        
        payload = {
            "user_id": user_id,
            "ttl_sec": 604800,
            "mark_email_as_verified": True
        }
        
        headers = {
            "Authorization": f"Bearer {m2m_token}",
            "Content-Type": "application/json"
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(ticket_url, json=payload, headers=headers)
            response.raise_for_status()
            
        logger.info("password_reset_sent", user_id=user_id)
        return response.json()
        
    except httpx.HTTPStatusError as e:
        logger.error(
            "password_reset_http_error",
            user_id=user_id,
            status_code=e.response.status_code,
            response=e.response.text,
            retry_count=self.request.retries
        )
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    except httpx.RequestError as e:
        logger.error(
            "password_reset_network_error",
            user_id=user_id,
            error=str(e),
            retry_count=self.request.retries
        )
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    except Exception as e:
        logger.error(
            "password_reset_unexpected_error",
            user_id=user_id,
            error=str(e),
            error_type=type(e).__name__,
            retry_count=self.request.retries
        )
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    

@celery_app.task(bind=True, max_retries=3)
def send_verification_email_task(self, email: str, name: str):
    try:
        
        
        formatted_email = VERIFICATION_EMAIL.format(name=name)
        email_req = type('obj', (object,), {'email': email})()
        send_email(email_req, formatted_email)
        
        logger.info("verification_email_sent", email=email)
        return {"status": "success", "email": email}
        
    except Exception as e:
        logger.error(
            "verification_email_failed",
            email=email,
            error=str(e),
            error_type=type(e).__name__,
            retry_count=self.request.retries
        )
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))