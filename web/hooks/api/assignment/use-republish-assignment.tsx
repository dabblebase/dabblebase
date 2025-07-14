import { api } from "@/utils/api";
import { useQueryClient } from "@tanstack/react-query";

export function useRepublishAssignment() {
  const queryClient = useQueryClient();

  const { mutate: republishAssignment } = api.useMutation(
    "put",
    "/api/assignment/{assignment_id}/republish"
  );

  const refetchOnSuccess = () => {
    queryClient.refetchQueries({
      queryKey: ["get", "/api/assignment/{assignment_id}/staff-view"],
    });
    queryClient.refetchQueries({
      queryKey: ["get", "/api/assignment/dropdown"],
    });
  };

  return { republishAssignment, refetchOnSuccess };
}
