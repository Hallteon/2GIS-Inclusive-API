import asyncio
import uvloop

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from settings import config_parameters, is_prod
from starlette.middleware.cors import CORSMiddleware

from api.database import engine
from api.routers.blind_routes import router
from admin.admin_global import AdminAuth, admin_models


def create_app() -> FastAPI:
    docs_url = '/docs' if not config_parameters.IS_PROD else None
    redoc_url = '/redoc' if not config_parameters.IS_PROD else None
    app = FastAPI(title='2gis_for_everyone.API', debug=not config_parameters.IS_PROD,
                  docs_url=docs_url, redoc_url=redoc_url,
                  root_path='/api')

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['http://localhost:3000'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SessionMiddleware, secret_key=config_parameters.SECRET_KEY)
    app.mount('/static', StaticFiles(directory=config_parameters.STATIC_DIR), name='static')

    return app

uvloop.install()
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
server = create_app()

server.include_router(router)

admin = Admin(app=server, engine=engine, authentication_backend=AdminAuth(config_parameters.SECRET_KEY))

if is_prod:
    print('PROD')


@server.on_event('startup')
async def on_startup_():
    for model in admin_models:
        admin.add_view(model)
