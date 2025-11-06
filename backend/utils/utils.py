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
brevo_api_key = config.get("brevo_api_key") 


async def send_email(req, html_content):
    """Send custom email using Brevo API"""
    
    if not brevo_api_key:
        print("Warning: Brevo API key not configured")
        raise HTTPException(status_code=500, detail="Email service not configured")
    
    brevo_api_url = "https://api.brevo.com/v3/smtp/email"
    
    headers = {
        "accept": "application/json",
        "api-key": brevo_api_key,  
        "content-type": "application/json"
    }
    
    payload = {
        "sender": {
            "name": "Kaban App",
            "email": "king.ibadmad@gmail.com"  
        },
        "to": [
            {
                "email": req.email,
                "name": req.name
            }
        ],
        "subject": "Verify your email address",
        "htmlContent": html_content  # ⭐ Changed: removed curly braces
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
                status_code=500,
                detail="Failed to send verification email"
            )
        except Exception as e:
            print(f"Unexpected error sending email: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to send verification email"
            )
        


@alru_cache(maxsize=1)
async def get_management_api_token():
    auth0_token_url = f"https://{auth0_domain}/oauth/token"
    
    payload = {
        "client_id": auth0_m2m_client_id,       
        "client_secret": auth0_m2m_client_secret,
        "audience": f"https://{auth0_domain}/api/v2/",
        "grant_type": "client_credentials"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(auth0_token_url, json=payload)
        return response.json()["access_token"]