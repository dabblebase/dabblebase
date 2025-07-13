import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import ErrorMessage from "@/components/errors/error-message";
import { Fragment } from "react";
import CreateAssignmentGroupDialog from "./create-assignment-group-dialog";
import AssignmentGroupUnassignedStudentSelector from "./assignment-group-unassigned-student-selector";
import AssignmentGroupManagerRow from "./assignment-group-manager-row";
import { useGroupData } from "@/hooks/api/assignment/groups/use-group-data";
import { useAddGroupMember } from "@/hooks/api/assignment/groups/use-add-group-member";

export default function AssignmentGroupManager({
  courseId,
  assignmentId,
  refetch,
}: {
  courseId: number;
  assignmentId: number;
  refetch: () => void;
}) {
  const { groupData, groupDataError } = useGroupData(assignmentId);

  const { addGroupMember } = useAddGroupMember();

  type OnSubmitHandler = (
    groupId: number,
    setOpen: (newValue: boolean) => void
  ) => void;
  const onAddStudentToGroup: (studentId: number) => OnSubmitHandler = (
    studentId: number
  ) => {
    return (groupId: number, setOpen: (newValue: boolean) => void) => {
      addGroupMember(
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
            refetch();
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
              {groupData.groups.length === 0 && (
                <p className="text-accent-foreground/80">
                  No groups have been created yet - create one now!
                </p>
              )}
              {groupData.groups.map((group, index) => (
                <Fragment key={group.group_id}>
                  <AssignmentGroupManagerRow
                    courseId={courseId}
                    assignmentId={assignmentId}
                    group={group}
                    refetch={refetch}
                  />
                  {index < groupData.groups.length - 1 && (
                    <Separator className="my-2" />
                  )}
                </Fragment>
              ))}
            </CardContent>
          </Card>
          <div>
            <CreateAssignmentGroupDialog
              assignmentId={assignmentId}
              refetch={refetch}
            >
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
