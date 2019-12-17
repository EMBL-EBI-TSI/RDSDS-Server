from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from app.business.globus import login


router = APIRouter()

@router.get(
    '/login', 
     name='globus_login',
     summary="Login for Globus Service",
     tags=["GlobusLogin"]
)
async def globus_login(request: Request):
    """
    Login via Globus Auth.
    May be invoked in one of two scenarios:

      1. Login is starting, no state in Globus Auth yet
      2. Returning to application during login, already have short-lived
         code from Globus Auth to exchange for tokens, encoded in a query
         param
    """
    return await login(request)
