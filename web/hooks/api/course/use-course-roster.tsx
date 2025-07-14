import { api } from "@/utils/api";

export function useCourseRoster(courseId: number) {
  const {
    data: rosterData,
    isLoading: rosterLoading,
    isError: rosterError,
  } = api.useQuery("get", "/api/course/{course_id}/roster", {
    params: { path: { course_id: courseId } },
  });

  return { rosterData, rosterLoading, rosterError };
}
