import { api } from "@/utils/api";
import { useQueryClient } from "@tanstack/react-query";

export function useChangeMemberRole() {
  const queryClient = useQueryClient();

  const { mutate: changeMemberRole } = api.useMutation(
    "put",
    "/api/course/{course_id}/member/{user_id}/role"
  );

  const refetchOnSuccess = () => {
    queryClient.refetchQueries({
      queryKey: ["get", "/api/course/{course_id}/roster"],
    });
  };
  return {
    changeMemberRole,
    refetchOnSuccess,
  };
}
