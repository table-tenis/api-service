from urllib.request import HTTPBasicAuthHandler
from fastapi import FastAPI, Request, Response

import time
from routes.enterprise import enterprise_router
from routes.camera import camera_router
from routes.site import site_router
from routes.staff import staff_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
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
from h11._util import LocalProtocolError
description = """
            Enterprise Manager
        """

app = FastAPI(description=description)

origins = [
    "http://172.21.100.174:8081",
    "https://172.21.100.174:8080"
]
# class MyMiddleware:
#     def __init__(
#         self, app: ASGIApp, dispatch: typing.Optional[DispatchFunction] = None
#     ) -> None:
#         self.app = app
#         self.dispatch_func = self.dispatch if dispatch is None else dispatch

#     async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
#         await self.app(scope, receive, send)
#         return
#     async def dispatch(self, request: Request, call_next):
#         # do something with the request object, for example
#         content_type = request.headers.get('Content-Type')
#         print("================= dispatch", content_type)
        
#         # process the request and get the response    
#         response = await call_next(request)
        
#         return response

# app.add_middleware(BaseHTTPMiddleware, some_attribute="some_attribute_here_if_needed")

# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     start_time = time.time()
#     print("In MiddleWare")
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     # response.headers["X-Process-Time"] = str(f'{process_time} sec')#str(f'{process_time:0.10f} sec')
#     # response.set_cookie(key="fakesession", value="fake-cookie-session-value")
#     if response.status_code >= 400:
#         print("reponse error status_code = ", response.status_code)
#     # print("=========== Return Response, response header = ", response.headers)
#     return response

app.include_router(enterprise_router, prefix="/api/xface/v1/enterprises")
app.include_router(camera_router, prefix="/api/xface/v1/cameras")
app.include_router(site_router, prefix="/api/xface/v1/sites")
app.include_router(staff_router, prefix="/api/xface/v1/staffs")
if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.SERVICE_HOST, port=settings.SERVICE_PORT, reload=True)
    # config = hypercorn.config.Config()
    # config._bind = ["172.21.100.174:9083"]
    # from hypercorn.asyncio import serve
    # asyncio.run(serve(app, config=config))

