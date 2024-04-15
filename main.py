from typing import Union

from fastapi import FastAPI
from api.v1 import api as api_v1

app = FastAPI()

app.include_router(api_v1.router)