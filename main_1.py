from datetime import datetime
from enum import Enum
import os
from pathlib import Path  # python3 only
from pprint import pprint
from typing import Dict, List

import databases
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
import sqlalchemy
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

env_path = Path('.env')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
