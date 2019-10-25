import os
from datetime import datetime
from enum import Enum
from pprint import pprint
from typing import Dict, List

import databases
import sqlalchemy
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.gzip import GZipMiddleware

from dotenv import load_dotenv
from pathlib import Path  # python3 only
env_path = Path('.env')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)