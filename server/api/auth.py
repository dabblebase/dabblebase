"""Auth endpoint for the web application."""

import requests
from fastapi import APIRouter, Depends
from fastapi.responses import Response, RedirectResponse
from fastapi.exceptions import HTTPException
from ..env import env
from ..services import ProjectAuthService
from ..entities import UserAuthenticationProvider
from datetime import datetime, timedelta, timezone
from ..services.project import auth_crypto as crypto

tag = "Authentication"
openapi_tags = {
    "name": tag,
    "description": "Production systems monitor these endpoints upon deployment, and at regular intervals, to ensure the service is running.",
}

api = APIRouter(prefix="/auth")

UNC_AUTH_SERVER_HOST = "csxl.unc.edu"


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
    continue_to: str = "/",
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
    user = project_auth_svc.get_or_create_user(pid, UserAuthenticationProvider.UNC_SSO)

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
