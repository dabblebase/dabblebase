import { Trash, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useState } from "react";
import RenameComponent from "@/components/ui/rename";
import type { components } from "@/models/schema";
import { api } from "@/utils/api";
import DeleteAssignmentGroupDialog from "./delete-assignment-group-dialog";
import AssignmentGroupStudentSelector from "./assignment-group-student-selector";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";

type AssignmentGroup = components["schemas"]["GetGroupsResponse_Group"];

export default function AssignmentGroupManagerRow({
  courseId,
  assignmentId,
  group,
  refetch,
}: {
  courseId: number;
  assignmentId: number;
  group: AssignmentGroup;
  refetch: () => void;
}) {
  const queryClient = useQueryClient();

  // Hooks and mutations for renaming the group
  const [renameText, setRenameText] = useState(group.group_name);
  const { mutate: renameGroup } = api.useMutation(
    "put",
    "/api/assignment/{assignment_id}/group/{group_id}/rename"
  );
  const renamingGroupHandler = (setRenaming: (renaming: boolean) => void) => {
    renameGroup(
      {
        params: {
          path: {
            assignment_id: assignmentId,
            group_id: group.group_id,
          },
          query: {
            name: renameText,
          },
        },
      },
      {
        onSuccess: () => {
          setRenaming(false);
          // Refetch the group data to reflect the changes
          refetch();
        },
      }
    );
  };

  // Hooks and mutations for removing group members
  const { mutate: removeGroupMember } = api.useMutation(
    "delete",
    "/api/assignment/{assignment_id}/group/{group_id}/member/{user_id}"
  );
  const onRemoveGroupMember = (userId: number) => {
    removeGroupMember(
      {
        params: {
          path: {
            assignment_id: assignmentId,
            group_id: group.group_id,
            user_id: userId,
          },
        },
      },
      {
        onSuccess: () => {
          // Refetch the group data to reflect the changes
          refetch();
          // Refetch the search to ensure that the student is no longer listed
          queryClient.refetchQueries({
            queryKey: ["get", "/api/course/{course_id}/students"],
          });
        },
        onError: () => {
          toast.error("Failed to remove group member", {
            description: "Please try again later.",
          });
        },
      }
    );
  };

  return (
    <div className="flex flex-row w-full items-center">
      <div className="flex flex-row min-w-fit items-center gap-3">
        <RenameComponent
          initialValue={group.group_name}
          value={renameText}
          setValue={setRenameText}
          placeholder="Enter group name"
          onRename={renamingGroupHandler}
          inputWidth="80px"
          customNameClassName="font-medium"
        />
        <Separator
          orientation="vertical"
          className="data-[orientation=vertical]:h-6 mr-3"
        />
      </div>

      <div className="flex flex-row items-center gap-3 ml-auto">
        <div className="flex flex-row flex-wrap items-center gap-2">
          {group.members.map((member) => (
            <Button
              key={member.user_id}
              variant="outline"
              size="sm"
              className="group"
              onClick={() => onRemoveGroupMember(member.user_id)}
            >
              <span className="group-hover:line-through group-hover:text-accent-foreground/80 group-hover:decoration-accent-foreground/80 transition-all">
                {member.user_name}
              </span>
              <X className="hidden group-hover:block transition-opacity cursor-pointer" />
            </Button>
          ))}
          <AssignmentGroupStudentSelector
            courseId={courseId}
            assignmentId={assignmentId}
            groupId={group.group_id}
            refetch={refetch}
          />
        </div>
        <Separator
          orientation="vertical"
          className="data-[orientation=vertical]:h-6"
        />
        <DeleteAssignmentGroupDialog
          assignmentId={assignmentId}
          groupId={group.group_id}
          refetch={refetch}
        >
          <Button variant="destructive" size="icon">
            <Trash />
          </Button>
        </DeleteAssignmentGroupDialog>
      </div>
    </div>
  );
}
