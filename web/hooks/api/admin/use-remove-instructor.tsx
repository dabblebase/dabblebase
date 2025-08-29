import { api } from "@/utils/api";
import { useQueryClient } from "@tanstack/react-query";

export function useRemoveInstructor() {
  const queryClient = useQueryClient();

  const { mutate: removeInstructor } = api.useMutation(
    "put",
    "/api/admin/instructor/remove"
  );

  const refetchOnSuccess = () => {
    queryClient.refetchQueries({
      queryKey: ["get", "/api/admin/users"],
    });
  };
  return {
    removeInstructor,
    refetchOnSuccess,
  };
}
