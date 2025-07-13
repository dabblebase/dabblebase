import { api } from "@/utils/api";

export function useAssignments(courseId: number) {
  const {
    data: assignmentsData,
    isLoading: assignmentsLoading,
    error: assignmentsError,
  } = api.useQuery("get", "/api/course/{course_id}/assignments", {
    params: { path: { course_id: courseId } },
  });

  const noAssignmentsFound =
    !!assignmentsData && assignmentsData.assignments.length === 0;

  return {
    assignmentsData,
    assignmentsLoading,
    assignmentsError,
    noAssignmentsFound,
  };
}
