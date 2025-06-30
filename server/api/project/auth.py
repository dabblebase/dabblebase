"""Auth endpoints for projects."""

import requests
from fastapi import APIRouter, Depends
from fastapi.responses import Response, RedirectResponse
from fastapi.exceptions import HTTPException
from ..project import tag
from ...env import env
from ...services import ProjectAuthService
from ...entities import UserAuthenticationProvider

api = APIRouter(prefix="/api/project/{project_id}/auth")

UNC_AUTH_SERVER_HOST = "csxl.unc.edu"


@api.get("/unc", tags=[tag])
def auth_unc(project_id: int, continue_to: str = "/"):
    """
    This endpoint initiates authentication to the UNC SSO proxy for a project. The proxy will
    respond with an authorization token and call the `/unc/callback` endpoint for Tinkerbase
    to continue the UNC SSO authentication flow.
    """
    origin = f"{env.HOST}/api/project/{project_id}/auth/callback"
    return RedirectResponse(
        f"https://{UNC_AUTH_SERVER_HOST}/auth?origin={origin}&continue_to={continue_to}"
    )


@api.get("/unc/callback", tags=[tag])
def auth_unc_callback(
    project_id: int,
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
    pid = body["pid"]
    user = project_auth_svc.get_or_create_user(pid, UserAuthenticationProvider.UNC_SSO)

    # Issue a new JWT token on behalf of Tinkerbase for the user to be authenticated with
    # the project, signed with the project's private auth key.
    jwt_token = project_auth_svc.generate_token_for_project_auth_request(
        project_id, user.id
    )

    return _generate_auth_response(jwt_token, continue_to)


def _generate_auth_response(token: str, continue_to: str) -> Response:
    """
    Generate an HTML response to be sent to the client after authentication, which
    contains JavaScript to store the JWT token in localStorage and redirect the user
    """

    html = f"""
    <html>
        <head>
            <title>Authenticating...</title>
        </head>
        <body>
            <h1>Authenticating...</h1>
            <script type='application/javascript'>
                localStorage.setItem('bearerToken', '{token}');
                window.location.href = '{continue_to}';
            </script>
        </body>
    </html>
    """

    return Response(
        content=html,
        media_type="text/html",
        headers={"Cache-Control": "no-cache"},
    )
