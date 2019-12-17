import json
import logging

from app.core.config import ELIXIR_CLIENT_ID, ELIXIR_CLIENT_SECRET, ELIXIR_METADATA_URL
from app.business.oauth import auth, login, logout
from fastapi import APIRouter
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request

router = APIRouter()

@router.get(
    '/login', 
     name='oauth_login_api',
     summary="Login API for OAuth",
     tags=["OAuth"]
)
async def login_api(request: Request):
    return await login(request)


@router.get(
    '/auth', 
     name='oauth_login_auth',
     summary="Auth API for OAuth",
     tags=["OAuth"]
)
async def auth_api(request: Request):
    return await auth(request)
    


@router.get(
    '/logout', 
     name='oauth_logout_auth',
     summary="LogOut API for OAuth",
     tags=["OAuth"]
)
async def logout_api(request: Request):
    return await logout(request)

