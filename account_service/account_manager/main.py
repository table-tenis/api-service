from fastapi import FastAPI, Request

import time
from routes.account import account_router
from routes.admin import admin_router
import uvicorn
import hypercorn
from core.database import Settings
description = \
"""
    Account API To Manager System Accessing.
"""

app = FastAPI(description=description)

origins = [
    "http://172.21.100.174:8081",
    "https://172.21.100.174:8080"
]

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f'{process_time} sec')#str(f'{process_time:0.10f} sec')
    return response

app.include_router(account_router, prefix="/api/xface/v1/acc/accounts")
app.include_router(admin_router, prefix="/api/xface/v1/acc/admin")
if __name__ == "__main__":
    uvicorn.run("main:app", host="172.21.100.174", port=9082, reload=True)

