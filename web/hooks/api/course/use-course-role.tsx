import { api } from "@/utils/api";

export function useCourseRole(courseId: number) {
  const { data: courseRoleData } = api.useQuery(
    "get",
    "/api/course/{course_id}/role",
    {
      params: { path: { course_id: courseId } },
    }
  );

  return { courseRoleData };
}
