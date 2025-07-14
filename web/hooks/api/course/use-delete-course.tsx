import { api } from "@/utils/api";

export function useDeleteCourse() {
  const { mutate: deleteCourse } = api.useMutation(
    "delete",
    "/api/course/{course_id}"
  );

  return { deleteCourse };
}
