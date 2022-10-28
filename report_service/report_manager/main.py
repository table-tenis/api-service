from fastapi import FastAPI, Request, Response

import time
from routes.report import report_router
from starlette.types import ASGIApp, Receive, Scope, Send
import typing
RequestResponseEndpoint = typing.Callable[[Request], typing.Awaitable[Response]]
DispatchFunction = typing.Callable[
    [Request, RequestResponseEndpoint], typing.Awaitable[Response]
]
# from routes.events import event_router
import uvicorn
import hypercorn
import ssl
import asyncio
from config.config import settings
from routes.report_graphql import graphql_app
from test_graphqlapp import graph_router
description = """
            Reports Manager
        """

app = FastAPI(description=description)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # data = await request.json()
    # print("middleware data = ", data['query'])
    # print("query_params = " ,request.query_params)
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f'{process_time} sec')#str(f'{process_time:0.10f} sec')
    # response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    if response.status_code >= 400:
        print("reponse error status_code = ", response.status_code)
    # print("=========== Return Response, response header = ", response.headers)
    return response

@app.get("/")
async def healthcheck():
    return {"message": "Ok"}

origins = [
    "http://172.21.100.174:8081",
    "https://172.21.100.174:8080"
]

app.include_router(report_router, prefix="/api/xface/v1/reports")
app.include_router(graphql_app, prefix="/graphql")
app.include_router(graph_router, prefix="/test_graphql")
if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.SERVICE_HOST, port=settings.SERVICE_PORT, reload=True)
    # config = hypercorn.config.Config()
    # config._bind = ["172.21.100.174:9083"]
    # from hypercorn.asyncio import serve
    # asyncio.run(serve(app, config=config))

