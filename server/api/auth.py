"""Auth endpoint for the web application."""

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import requests
from fastapi import APIRouter, Depends, Cookie, Security
from fastapi.responses import Response, RedirectResponse
from fastapi.exceptions import HTTPException
from ..env import env
from ..services import ProjectAuthService
from ..entities import UserAuthenticationProvider
from datetime import datetime, timedelta, timezone
from ..services.project import auth_crypto as crypto
from ..models.auth import Subject

tag = "Authentication"
openapi_tags = {
    "name": tag,
    "description": "API endpoint for authentication for the web application",
}

api = APIRouter(prefix="/auth")

UNC_AUTH_SERVER_HOST = "csxl.unc.edu"


def registered_user(
    bearer_token: HTTPAuthorizationCredentials | None = Security(
        HTTPBearer(auto_error=False)
    ),
    auth_token: str = Cookie(default=None, alias="auth-token", include_in_schema=False),
) -> Subject:
    # The bearer token is used for direct API requests via the docs page, the
    # auth token is used for requests from the web application.
    token = bearer_token.credentials if bearer_token else auth_token

    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        payload = crypto.decode_jwt_with_symmetric_key(token, env.AUTH_MASTER_SECRET)
        return Subject(id=payload["id"])
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")


def registered_user_or_none(
    bearer_token: HTTPAuthorizationCredentials | None = Security(
        HTTPBearer(auto_error=False)
    ),
    auth_token: str = Cookie(default=None, alias="auth-token", include_in_schema=False),
) -> Subject | None:
    # The bearer token is used for direct API requests via the docs page, the
    # auth token is used for requests from the web application.
    token = bearer_token.credentials if bearer_token else auth_token

    if not token:
        return None
    try:
        payload = crypto.decode_jwt_with_symmetric_key(token, env.AUTH_MASTER_SECRET)
        return Subject(id=payload["id"])
    except Exception:
        return None


@api.get("/unc", tags=[tag], include_in_schema=False)
def auth_unc(continue_to: str = "/"):
    """
    This endpoint initiates authentication to the UNC SSO proxy for a project. The proxy will
    respond with an authorization token and call the `/unc/callback` endpoint for Tinkerbase
    to continue the UNC SSO authentication flow.
    """
    origin = f"{env.HOST}/auth/unc/callback"
    return RedirectResponse(
        f"https://{UNC_AUTH_SERVER_HOST}/auth?origin={origin}&continue_to={continue_to}"
    )


@api.get("/unc/callback", tags=[tag], include_in_schema=False)
def auth_unc_callback(
    token: str,
    continue_to: str = "/dashboard",
    project_auth_svc: ProjectAuthService = Depends(),
):
    """
    This endpoint is called by the UNC SSO proxy after the user has authenticated with UNC SSO.
    Tinkerbase will verify the token and issue a JWT token for the user to be authenticated.
    """
    # Verify that the token provided is valid and originated from the UNC SSO proxy
    params = {"token": token}
    response = requests.get(f"https://{UNC_AUTH_SERVER_HOST}/verify", params=params)

    if response.status_code != requests.codes.ok:
        raise HTTPException(
            status_code=401, detail="Token could not be verified with UNC SSO."
        )

    # Extract the UNC PID from the UNC SSO proxy and use it to create or retrieve a user
    body = response.json()
    pid = str(body["pid"])
    username = str(body["uid"])
    first_name = ""
    last_name = ""
    email = ""

    # Retrieve the user's name and email from the UNC directory
    try:
        user_info_response = requests.get(f"https://directory.unc.edu/api/search/{pid}")
        if user_info_response.status_code != requests.codes.ok:
            raise HTTPException(
                status_code=401,
                detail="Could not retrieve user information from UNC directory.",
            )
        user_info = user_info_response.json()[0]
        first_name = (
            str(user_info["givenNameIterator"][0])
            if "givenNameIterator" in user_info
            and isinstance(user_info["givenNameIterator"], list)
            and len(user_info["givenNameIterator"]) > 0
            else ""
        )
        last_name = (
            str(user_info["snIterator"][0])
            if "snIterator" in user_info
            and isinstance(user_info["snIterator"], list)
            and len(user_info["snIterator"]) > 0
            else ""
        )
        email = (
            str(user_info["mailIterator"][0])
            if "mailIterator" in user_info
            and isinstance(user_info["mailIterator"], list)
            and len(user_info["mailIterator"]) > 0
            else ""
        )
    except Exception as e:
        raise e

    user = project_auth_svc.get_or_create_user(
        auth_identifier=pid,
        first_name=first_name,
        last_name=last_name,
        email=email,
        username=username,
        auth_provider=UserAuthenticationProvider.UNC_SSO,
    )

    # Issue a new JWT token on behalf of Tinkerbase for the user to be authenticated with
    # the project, signed with the project's private auth key.
    jwt_token = _generate_token_for_auth_request(user.id)

    # Return a response that contains the JWT token and redirects the user while setting
    # the token in cookies.
    response = RedirectResponse(url=continue_to)
    one_month = 60 * 60 * 24 * 30
    expires = (datetime.now(timezone.utc) + timedelta(seconds=one_month)).strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    response.set_cookie(
        key="auth-token",
        value=jwt_token,
        httponly=True,
        secure=False,  # Required for development purposes since student apps will run on localhost
        samesite="lax",
        max_age=one_month,
        expires=expires,
        path="/",
    )

    return response


@api.get("/as/{user_id}", include_in_schema=False)
def auth_as(user_id: int, continue_to: str = "/dashboard"):
    """Authorizes as a specific user by generating a token for them - only in development mode."""
    # Verify development mode
    if not env.MODE == "development":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only available in development mode.",
        )

    # Sign JWT
    jwt_token = _generate_token_for_auth_request(user_id)
    response = RedirectResponse(url=continue_to)
    one_month = 60 * 60 * 24 * 30
    expires = (datetime.now(timezone.utc) + timedelta(seconds=one_month)).strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    response.set_cookie(
        key="auth-token",
        value=jwt_token,
        httponly=True,
        secure=False,  # Required for development purposes since student apps will run on localhost
        samesite="lax",
        max_age=one_month,
        expires=expires,
        path="/",
    )

    return response


@api.post("/logout")
def logout(response: Response):
    """
    Logs out the user by clearing the auth token cookie.
    """
    response.delete_cookie("auth-token", path="/")
    return {"message": "Logged out successfully."}


def _generate_token_for_auth_request(user_id: int) -> str:
    """
    Generates a token for a user to authenticate with a project. Unlike auth with projects,
    this token is signed using the auth secret and signed symmetrically.
    """

    # Retrieve the project's encrypted private authentication key and decrypt it.
    # Recall the encryption key was derived from the master secret and project ID.
    payload = {"id": user_id}
    token = crypto.sign_jwt_with_symmetric_key(payload, env.AUTH_MASTER_SECRET)
    return token
