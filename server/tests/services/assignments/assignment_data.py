"""Data models specific to course testing"""

from ..seed import course, instructor_user, draft_indiv_assignment
from ....models.assignment import *

create_draft_request = CreateDraftRequest(
    name="Sample Assignment",
    course_id=course.id,
    is_group=False,
)

rename_request = RenameRequest(
    assignment_id=draft_indiv_assignment.id,
    name="Renamed Assignment",
)

rename_request_name_empty = RenameRequest(
    assignment_id=draft_indiv_assignment.id,
    name="",
)

rename_request_not_found = RenameRequest(
    assignment_id=404,
    name="Renamed Assignment",
)
