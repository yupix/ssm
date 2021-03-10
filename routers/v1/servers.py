from fastapi import APIRouter
from fastapi_versioning import versioned_api_route

router = APIRouter(route_class=versioned_api_route(1))


@router.get('/')
async def index() -> dict:
	"""Topページ"""
	return {"body": {"type": "text", "text": "Welcome to the API Version 1"}}


@router.get('/server_info/{server_id}')
async def server_info(server_id: int) -> dict:
	"""与えられたサーバーIDからサーバーの基本情報を返します"""
	return {"body": {"type": "info", "server": {"name": "test"}}}
