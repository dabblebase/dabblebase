import { api } from "@/utils/api";
import { useQueryClient } from "@tanstack/react-query";

export function useAddInstructor() {
  const queryClient = useQueryClient();

  const { mutate: addInstructor } = api.useMutation(
    "put",
    "/api/admin/instructor/add"
  );

  const refetchOnSuccess = () => {
    queryClient.refetchQueries({
      queryKey: ["get", "/api/admin/users"],
    });
  };
  return {
    addInstructor,
    refetchOnSuccess,
  };
}
