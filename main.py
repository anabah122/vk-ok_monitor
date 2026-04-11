import sys 
sys.dont_write_bytecode = True 

from fastapi import FastAPI, Depends
import logger  # отключает логи на /stats/*

app = FastAPI()

# Auth
from auth_service.auth_core import require_auth
from auth_service.auth_router import router as auth_router
app.include_router(auth_router)


# Frontend (требует авторизации)
from frontend_service.main_router import router as main_router
from frontend_service.stats.stats_router import router as stats_router
app.include_router(main_router, dependencies=[Depends(require_auth)])
app.include_router(stats_router, prefix="/stats", dependencies=[Depends(require_auth)])


# API /api/* 
from api_service.api_router import api_router
app.include_router(api_router, prefix="/api")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)


# ssh root@85.204.240.73
# cd /app && git pull origin main && docker compose up -d --build
# docker logs app-app-1