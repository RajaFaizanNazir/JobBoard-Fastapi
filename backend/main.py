from apis.base import api_router
from core.config import settings
from db.base import Base
from db.session import engine
from db.utils import check_db_connected
from db.utils import check_db_disconnected
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from webapps.base import api_router as web_app_router

from fastapi.responses import RedirectResponse

from fastapi import FastAPI, Depends
from fastapi_keycloak import FastAPIKeycloak, OIDCUser, UsernamePassword, HTTPMethod, KeycloakUser, KeycloakGroup



from datetime import timedelta

from apis.utils import OAuth2PasswordBearerWithCookie
from core.config import settings
from core.hashing import Hasher
from core.security import create_access_token
from db.repository.login import get_user
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from jose import JWTError
from schemas.tokens import Token
from sqlalchemy.orm import Session

def include_router(app):
    app.include_router(api_router)
    app.include_router(web_app_router)


def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")


def create_tables():
    Base.metadata.create_all(bind=engine)


def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    
    

    include_router(app)
    configure_static(app)
    create_tables()
    return app


app = start_application()
idp = FastAPIKeycloak(
        server_url="http://localhost:8080/auth",
        client_id="test-client",
        client_secret="GzgACcJzhzQ4j8kWhmhazt7WSdxDVUyE",
        admin_client_secret="BIcczGsZ6I8W5zf0rZg5qSexlloQLPKB",
        realm="Test",
        callback_uri="http://localhost:8000/callback"
    )
idp.add_swagger_config(app)


# @app.get("/login/")
# def login_redirect():
#     return RedirectResponse(idp.login_uri)


@app.on_event("startup")
async def app_startup():
    await check_db_connected()


@app.on_event("shutdown")
async def app_shutdown():
    await check_db_disconnected()



@app.post("/login/", tags=["user-request"])
def login(user: UsernamePassword = Depends()):
    return idp.user_login(username=user.username, password=user.password.get_secret_value())

@app.get("/login-link", tags=["auth-flow"])
def login_redirect():
    return idp.login_uri


@app.get("/callback", tags=["auth-flow"])
def callback(session_state: str, code: str):
    return idp.exchange_authorization_code(session_state=session_state, code=code)


@app.get("/logout", tags=["auth-flow"])
def logout():
    return idp.logout_uri