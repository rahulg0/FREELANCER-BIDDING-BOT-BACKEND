import requests
from fastapi import APIRouter,Request
from starlette.responses import RedirectResponse
from requests_oauthlib import OAuth2Session
from app.config import settings

router = APIRouter()

client_id = settings.client_id
client_secret = settings.client_secret
authorization_base_url = settings.authorization_base_url
token_url = settings.token_url
redirect_uri = settings.redirect_uri

freelancer = OAuth2Session(client_id, redirect_uri=redirect_uri)



@router.get("/auth")
async def auth():
    authorization_url, state = freelancer.authorization_url(authorization_base_url)
    return RedirectResponse(authorization_url)


@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get('code') 
    
    if code:
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri
        }
        
        headers = {
            'content-type': 'application/x-www-form-urlencoded'
        }        
        response = requests.post(token_url, data=payload, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json() 
            return {"access_token": token_data}
        else:
            return {"error": "Failed to obtain access token", "details": response.text}
    else:
        return {"error": "Authorization code not found"}
