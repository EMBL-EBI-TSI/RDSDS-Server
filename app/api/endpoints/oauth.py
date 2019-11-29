import json
import logging

from app.core.config import ELIXIR_CLIENT_ID, ELIXIR_CLIENT_SECRET, ELIXIR_METADATA_URL
from fastapi import APIRouter, HTTPException
from starlette.config import Config
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth

router = APIRouter()

config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='elixir',
    server_metadata_url=ELIXIR_METADATA_URL,
    client_kwargs={
        'scope': 'openid email profile bona_fide_status'
    },
    client_id=ELIXIR_CLIENT_ID,
    client_secret=ELIXIR_CLIENT_SECRET
)


@router.get(
    '/', 
     name='oauth_login',
     summary="Login for OAuth",
     tags=["OAuthLogin"]
)
async def homepage(request: Request):
    logging.info('in homepage')
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            '<a href="/logout">logout</a>'
        )
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')


@router.get(
    '/login', 
     name='oauth_login_api',
     summary="Login API for OAuth",
     tags=["OAuthLogin"]
)
async def login(request: Request):
    redirect_uri = request.url_for('oauth_login_auth')
    return await oauth.elixir.authorize_redirect(request, redirect_uri)


@router.get(
    '/auth', 
     name='oauth_login_auth',
     summary="Login API for OAuth",
     tags=["OAuthLogin"]
)
async def auth(request: Request):
    token = await oauth.elixir.authorize_access_token(request)
    logging.info(token)
    user = await oauth.elixir.parse_id_token(request, token)
    logging.info(user)
    return RedirectResponse(url='/')


@router.get(
    '/logout', 
     name='oauth_logout_auth',
     summary="LogOut API for OAuth",
     tags=["OAuthLogOut"]
)
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

