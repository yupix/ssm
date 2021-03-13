import random
from fastapi import APIRouter
from fastapi_versioning import versioned_api_route

from base import db_manager
from settings import session
from sql.models.api import ApiRequests, ApiDetail

router = APIRouter(route_class=versioned_api_route(1))


@router.get('/')
async def index() -> dict:
	"""Topページ"""
	return {"body": {"type": "text", "text": "Welcome to the API Version 1"}}


@router.get('/server_info/{server_id}')
async def server_info(server_id: int, waiting_id: int = None) -> dict:
	"""与えられたサーバーIDからサーバーの基本情報を返します"""
	if waiting_id:
		check_completed = session.query(ApiDetail).filter(ApiDetail.request_id == waiting_id).first()
		if check_completed is not None and check_completed.content['result']['type'] == 'successful':
			return check_completed.content
	request_id = random.randrange(10 ** 10, 10 ** 11)
	content = {'server_id': server_id}
	await db_manager.commit(ApiRequests(request_id=request_id, type='server_info', request_content=content), autoincrement=True)

	return {"result": {"type": "waiting", "id": f"{request_id}"}}
# return {"body": {"type": "info", "server": {"name": "test"}}}
