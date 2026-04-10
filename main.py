from handler_servise.callback_action import CallbackAction
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import time

app = FastAPI()
import logger # disable logging on stats/json_data


from fastapi import Depends
from auth_service.auth_core import require_auth

from auth_service.auth_router import router as auth_router
app.include_router(auth_router)


from frontend_servise.main_router import router as main_router
from frontend_servise.stats.stats_router import router as stats_router, cache_instance

app.include_router(main_router, dependencies=[Depends(require_auth)])
app.include_router(stats_router, prefix="/stats", dependencies=[Depends(require_auth)])




action = CallbackAction(cache=cache_instance)

@app.post("/vk_callback")
async def callback_route(request: Request):
    data = await request.json()
    req = action.dispatch(data)
    return PlainTextResponse( req )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)

# ssh root@85.204.240.73
# cd /app && git pull origin main && docker compose up -d --build
# docker logs app-app-1