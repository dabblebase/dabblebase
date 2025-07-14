import { api } from "@/utils/api";
import { useQueryClient } from "@tanstack/react-query";

export function useRemoveGroupMember() {
  const queryClient = useQueryClient();

  const { mutate: removeGroupMember } = api.useMutation(
    "delete",
    "/api/assignment/{assignment_id}/group/{group_id}/member/{user_id}"
  );

  const refetchOnSuccess = () => {
    queryClient.refetchQueries({
      queryKey: ["get", "/api/course/{course_id}/students"],
    });
  };

  return { removeGroupMember, refetchOnSuccess };
}
