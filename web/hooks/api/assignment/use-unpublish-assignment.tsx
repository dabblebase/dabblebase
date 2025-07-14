import { api } from "@/utils/api";
import { useQueryClient } from "@tanstack/react-query";

export function useUnpublishAssignment() {
  const queryClient = useQueryClient();

  const { mutate: unpublishAssignment } = api.useMutation(
    "put",
    "/api/assignment/{assignment_id}/unpublish"
  );

  const refetchOnSuccess = () => {
    queryClient.refetchQueries({
      queryKey: ["get", "/api/assignment/{assignment_id}/staff-view"],
    });
    queryClient.refetchQueries({
      queryKey: ["get", "/api/assignment/dropdown"],
    });
  };
  return { unpublishAssignment, refetchOnSuccess };
}
