import { Plus } from "lucide-react";
import { Button } from "../../../../ui/button";
import { Card, CardContent } from "../../../../ui/card";
import { Separator } from "../../../../ui/separator";
import AssignmentGroupManagerRow from "./assignment-group-manager-row";
import { api } from "@/utils/api";
import ErrorMessage from "../../../../errors/error-message";
import { Fragment } from "react";
import CreateAssignmentGroupDialog from "./create-assignment-group-dialog";
import AssignmentGroupUnassignedStudentSelector from "./assignment-group-unassigned-student-selector";
import { useQueryClient } from "@tanstack/react-query";

export default function AssignmentGroupManager({
  courseId,
  assignmentId,
}: {
  courseId: number;
  assignmentId: number;
}) {
  const queryClient = useQueryClient();

  const { data: groupData, isError: groupDataError } = api.useQuery(
    "get",
    "/api/assignment/{assignment_id}/groups",
    {
      params: { path: { assignment_id: assignmentId } },
    }
  );

  const { mutate: addStudentToGroup } = api.useMutation(
    "post",
    "/api/assignment/{assignment_id}/group/{group_id}/member"
  );

  type OnSubmitHandler = (
    groupId: number,
    setOpen: (newValue: boolean) => void
  ) => void;
  const onAddStudentToGroup: (studentId: number) => OnSubmitHandler = (
    studentId: number
  ) => {
    return (groupId: number, setOpen: (newValue: boolean) => void) => {
      addStudentToGroup(
        {
          params: {
            path: { assignment_id: assignmentId },
          },
          body: {
            group_id: groupId,
            user_id: studentId,
          },
        },
        {
          onSuccess: () => {
            // Refetch the group data to reflect the changes
            queryClient.refetchQueries({
              queryKey: ["get", "/api/assignment/{assignment_id}/groups"],
            });
            setOpen(false);
          },
        }
      );
    };
  };

  return (
    <div className="flex flex-col gap-3">
      <p className="text-lg font-bold">Manage groups</p>
      {!!groupData && (
        <>
          <Card>
            <CardContent className="px-4">
              {groupData.groups.map((group, index) => (
                <Fragment key={group.group_id}>
                  <AssignmentGroupManagerRow
                    courseId={courseId}
                    assignmentId={assignmentId}
                    group={group}
                  />
                  {index < groupData.groups.length - 1 && (
                    <Separator className="my-2" />
                  )}
                </Fragment>
              ))}
            </CardContent>
          </Card>
          <div>
            <CreateAssignmentGroupDialog assignmentId={assignmentId}>
              <Button>
                <Plus />
                Add group
              </Button>
            </CreateAssignmentGroupDialog>
          </div>
          {groupData.unassigned_students.length > 0 && (
            <>
              <p className="font-semibold">
                Unassigned students ({groupData.unassigned_students.length})
              </p>
              <div className="flex flex-row flex-wrap gap-2">
                {groupData.unassigned_students.map((student) => (
                  <AssignmentGroupUnassignedStudentSelector
                    key={student.user_id}
                    groups={groupData.groups}
                    onSubmit={onAddStudentToGroup(student.user_id)}
                  >
                    <Button variant="outline" size="sm">
                      {student.user_name}
                    </Button>
                  </AssignmentGroupUnassignedStudentSelector>
                ))}
              </div>
            </>
          )}
        </>
      )}
      {groupDataError && <ErrorMessage resource="groups" />}
    </div>
  );
}
