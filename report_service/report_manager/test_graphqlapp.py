import asyncio
from multiprocessing.connection import wait
import re

import graphene
# from graphene_file_upload.scalars import Upload

from starlette.applications import Starlette
from starlette_graphene3 import GraphQLApp, make_graphiql_handler
from fastapi import APIRouter, Request
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    Union,
    cast,
)
from starlette.datastructures import UploadFile
import json


class User(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()


class Query(graphene.ObjectType):
    me = graphene.Field(User)

    def resolve_me(root, info, id):
        print("id = ", id)
        return {"id": "john", "name": "John"}


# class FileUploadMutation(graphene.Mutation):
#     class Arguments:
#         file = Upload(required=True)

#     ok = graphene.Boolean()

#     def mutate(self, info, file, **kwargs):
#         return FileUploadMutation(ok=True)


# class Mutation(graphene.ObjectType):
#     upload_file = FileUploadMutation.Field()


class Subscription(graphene.ObjectType):
    count = graphene.Int(upto=graphene.Int())

    async def subscribe_count(root, info, upto=3):
        for i in range(upto):
            yield i
            await asyncio.sleep(1)

schema = graphene.Schema(query=Query, subscription=Subscription)
graphql_app = GraphQLApp(schema=schema)

graph_router = APIRouter(tags=["Graph"])

async def _get_operation_from_request(
    request: Request,
) -> Union[Dict[str, Any], List[Any]]:
    content_type = request.headers.get("Content-Type", "").split(";")[0]
    print("content-type = ", content_type)
    request_body = await request.json()
    print("request body", request_body, type(request_body))
    if content_type == "application/json":
        try:
            return cast(Union[Dict[str, Any], List[Any]], await request.json())
        except (TypeError, ValueError):
            raise ValueError("Request body is not a valid JSON")
    elif content_type == "multipart/form-data":
        return await _get_operation_from_multipart(request)
    else:
        raise ValueError("Content-type must be application/json or multipart/form-data")


async def _get_operation_from_multipart(
    request: Request,
) -> Union[Dict[str, Any], List[Any]]:
    try:
        request_body = await request.form()
        print("request body", request_body)
    except Exception:
        raise ValueError("Request body is not a valid multipart/form-data")

    try:
        operations = json.loads(request_body.get("operations"))
    except (TypeError, ValueError):
        raise ValueError("'operations' must be a valid JSON")
    if not isinstance(operations, (dict, list)):
        raise ValueError("'operations' field must be an Object or an Array")

    try:
        name_path_map = json.loads(request_body.get("map"))
    except (TypeError, ValueError):
        raise ValueError("'map' field must be a valid JSON")
    if not isinstance(name_path_map, dict):
        raise ValueError("'map' field must be an Object")

    files = {k: v for (k, v) in request_body.items() if isinstance(v, UploadFile)}
    for (name, paths) in name_path_map.items():
        file = files.get(name)
        if not file:
            raise ValueError(
                f"File fields don't contain a valid UploadFile type for '{name}' mapping"
            )

        for path in paths:
            path = tuple(path.split("."))
            _inject_file_to_operations(operations, file, path)

    return operations


def _inject_file_to_operations(
    ops_tree: Any, _file: UploadFile, path: Sequence[str]
) -> None:
    k = path[0]
    key: Union[str, int]
    try:
        key = int(k)
    except ValueError:
        key = k
    if len(path) == 1:
        if ops_tree[key] is None:
            ops_tree[key] = _file
    else:
        _inject_file_to_operations(ops_tree[key], _file, path[1:])
        
""" Get reports """
@graph_router.post("/bytime")
async def report_bytime(request: Request):
    
    parse = await _get_operation_from_request(request)
    print("parse = ", parse, type(parse), " query = ", parse['query'], type(parse['query']))
    print("------------- Execute graphql app Here -----------------")
    return await graphql_app._handle_http_request(request)
    # data = await request.json()
    # print(data['query'], data['variables'])
    # result = schema.execute(data['query'], data['variables'])
    # return result