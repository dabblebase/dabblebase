"""Data models specific to course testing"""

from ..seed import (
    course,
    instructor_user,
)
from ....models.assignment import *

create_draft_request = CreateDraftRequest(
    name="Sample Assignment",
    course_id=course.id,
    is_group=False,
)
