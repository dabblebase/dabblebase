"""Data models specific to course testing"""

from ..seed import (
    course,
    instructor_user,
    draft_indiv_assignment,
    draft_group_assignment,
    group_assignment_group_1,
    group_assignment_group_1_member,
    student_1_user,
    student_2_user,
)
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

create_group_request = CreateGroupRequest(
    assignment_id=draft_group_assignment.id,
    group_name="Sample Group",
)

create_group_request_for_indiv = CreateGroupRequest(
    assignment_id=draft_indiv_assignment.id,
    group_name="Sample Group",
)

create_group_request_for_noname = CreateGroupRequest(
    assignment_id=draft_group_assignment.id,
    group_name="",
)

add_group_member_request = AddGroupMemberRequest(
    group_id=group_assignment_group_1.id, user_id=student_2_user.id
)

add_member_request_not_found = AddGroupMemberRequest(
    group_id=404, user_id=student_2_user.id
)

remove_group_member_request = RemoveGroupMemberRequest(
    group_id=group_assignment_group_1.id, user_id=student_1_user.id
)

remove_member_request_not_found = RemoveGroupMemberRequest(
    group_id=404, user_id=student_1_user.id
)

remove_member_request_not_found_user = RemoveGroupMemberRequest(
    group_id=group_assignment_group_1.id, user_id=404
)

delete_group_request = DeleteGroupRequest(group_id=group_assignment_group_1.id)

delete_group_request_not_found = DeleteGroupRequest(group_id=404)
