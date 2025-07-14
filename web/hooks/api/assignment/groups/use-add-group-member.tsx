import { api } from "@/utils/api";
import { useQueryClient } from "@tanstack/react-query";

export function useAddGroupMember() {
  const queryClient = useQueryClient();

  const { mutate: addGroupMember } = api.useMutation(
    "post",
    "/api/assignment/{assignment_id}/group/{group_id}/member"
  );

  const refetchOnSuccess = () => {
    queryClient.refetchQueries({
      queryKey: ["get", "/api/course/{course_id}/students"],
    });
  };
  return { addGroupMember, refetchOnSuccess };
}
