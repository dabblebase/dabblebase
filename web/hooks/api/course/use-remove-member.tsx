import { api } from "@/utils/api";
import { useQueryClient } from "@tanstack/react-query";

export function useRemoveMember() {
  const queryClient = useQueryClient();

  const { mutate: removeMember } = api.useMutation(
    "delete",
    "/api/course/{course_id}/member/{user_id}"
  );

  const refetchOnSuccess = () => {
    queryClient.refetchQueries({
      queryKey: ["get", "/api/course/{course_id}/roster"],
    });
  };
  return {
    removeMember,
    refetchOnSuccess,
  };
}
