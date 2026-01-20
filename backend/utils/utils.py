import httpx
from fastapi import HTTPException, Depends
from config.env import get_config
from functools import lru_cache
from async_lru import alru_cache


config = get_config()


auth0_domain = config["auth0_domain"]
auth0_client_id = config["auth0_client_id"]
auth0_m2m_client_id = config["auth0_m2m_client_id"]
auth0_m2m_client_secret = config["auth0_m2m_client_secret"]
brevo_sender_email=config["sender_email"]


async def send_email(req, html_content):
    """Send custom email using Brevo API"""
    
    # Load fresh config to get updated API key
    brevo_api_key = config.get("brevo_api_key")
    if not brevo_api_key:
        print("Warning: Brevo API key not configured")
        raise HTTPException(status_code=500, detail="Email service not configured")

    brevo_api_url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,
        "content-type": "application/json",
    }

    payload = {
        "sender": {"name": "Kaban App", "email": brevo_sender_email},
        "to": [{"email": req.email, "name": req.name}],
        "subject": "Verify your email address",
        "htmlContent": html_content,  # ⭐ Changed: removed curly braces
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(brevo_api_url, json=payload, headers=headers)
            response.raise_for_status()

            print(f"Email sent successfully to {req.email}")
            result = response.json()
            print(f"Email response: {result}")
            return result

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if e.response.text else str(e)
            print(f"Brevo API error: {error_detail}")
            raise HTTPException(
                status_code=500, detail="Failed to send verification email"
            )
        except Exception as e:
            print(f"Unexpected error sending email: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to send verification email"
            )


def send_email_sync(email_req, body: str):
    """Synchronous version for Celery tasks
    
    CRITICAL: Load brevo_api_key fresh in each call instead of using module-level variable.
    Reason: Celery worker subprocesses (prefork mode) inherit old module state from parent.
    Reading from /etc/secrets/BREVO_API_KEY file ensures we get the current value.
    """
    
    # Load config fresh (reads from /etc/secrets/BREVO_API_KEY file)
    fresh_config = get_config()
    brevo_api_key = fresh_config.get("brevo_api_key")
    
    if not brevo_api_key:
        raise ValueError("BREVO_API_KEY not configured in secrets")
    
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": brevo_api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "sender": {"email": fresh_config["sender_email"], "name": "Kaban App"},
        "to": [{"email": email_req.email}],
        "subject": "Welcome to Kaban",
        "htmlContent": body
    }
   
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

@alru_cache(maxsize=1)
async def get_management_api_token():
    auth0_token_url = f"https://{auth0_domain}/oauth/token"

    payload = {
        "client_id": auth0_m2m_client_id,
        "client_secret": auth0_m2m_client_secret,
        "audience": f"https://{auth0_domain}/api/v2/",
        "grant_type": "client_credentials",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(auth0_token_url, json=payload)
        return response.json()["access_token"]
