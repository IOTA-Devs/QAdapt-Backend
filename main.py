from fastapi import FastAPI
from routers import router
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.include_router(router.router)