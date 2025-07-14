import { api } from "@/utils/api";
import { useQueryClient } from "@tanstack/react-query";

export function useRenameAssignment() {
  const queryClient = useQueryClient();

  const { mutate: renameAssignment } = api.useMutation(
    "put",
    "/api/assignment/{assignment_id}/rename"
  );

  const refetchOnSuccess = () => {
    queryClient.refetchQueries({
      queryKey: ["get", "/api/assignment/{assignment_id}/draft"],
    });
    queryClient.refetchQueries({
      queryKey: ["get", "/api/assignment/dropdown"],
    });
    queryClient.refetchQueries({
      queryKey: ["get", "/api/assignment/{assignment_id}/staff-view"],
    });
  };

  return { renameAssignment, refetchOnSuccess };
}
