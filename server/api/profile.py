"""API endpoint for the user profile"""

from fastapi import APIRouter, Depends
from ..services import ProfileService
from ..api.auth import registered_user_or_none
from ..models.auth import Subject
from ..models.profile import GetProfileSummaryResponse

tag = "Profile"
openapi_tags = {
    "name": tag,
    "description": "API endpoint that loads profile data for the registered user.",
}

api = APIRouter(prefix="/api/profile")


@api.get("/summary", tags=[tag])
def get_summary(
    subject: Subject | None = Depends(registered_user_or_none),
    profile_svc: ProfileService = Depends(),
) -> GetProfileSummaryResponse | None:
    return profile_svc.get_profile_summary(subject)
