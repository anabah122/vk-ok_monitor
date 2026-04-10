from handler_servise.callback_action import CallbackAction
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import time

app = FastAPI()
import logger # disable logging on stats/json_data

from frontend_servise.stats_router import router as stats_router
app.include_router(stats_router, prefix="/stats")

action = CallbackAction()

@app.post("/vk_callback")
async def callback_route(request: Request):
    data = await request.json()
    req = action.dispatch(data)
    return PlainTextResponse( req )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)

#cd /app && git pull origin main && docker compose up -d --build
#docker logs app-app-1