import { api } from "@/utils/api";
import { useQueryClient } from "@tanstack/react-query";

export function useUpdateCourse() {
  const queryClient = useQueryClient();

  const { mutate: updateCourse } = api.useMutation(
    "put",
    "/api/course/{course_id}"
  );

  const refetchOnSuccess = () => {
    queryClient.refetchQueries({
      queryKey: ["get", "/api/course/{course_id}/staff-settings-view"],
    });
  };

  return {
    updateCourse,
    refetchOnSuccess,
  };
}
