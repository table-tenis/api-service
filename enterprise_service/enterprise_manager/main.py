from fastapi import FastAPI, Request

import time

from routes.enterprise import enterprise_router
from routes.camera import camera_router
from routes.site import site_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
# from routes.events import event_router
import uvicorn
import hypercorn
import ssl
import asyncio
description = """
            Enterprise Manager
        """

app = FastAPI(description=description)

origins = [
    "http://172.21.100.174:8081",
    "https://172.21.100.174:8080"
]


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    print("In MiddleWare")
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f'{process_time} sec')#str(f'{process_time:0.10f} sec')
    # response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    return response

app.include_router(enterprise_router, prefix="/api/xface/v1/enterprises")
app.include_router(camera_router, prefix="/api/xface/v1/cameras")
app.include_router(site_router, prefix="/api/xface/v1/sites")
if __name__ == "__main__":
    pass
    uvicorn.run("main:app", port=9083, reload=True)

