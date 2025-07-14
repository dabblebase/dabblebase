import { api } from "@/utils/api";

export function useStudents(
  courseId: number,
  assignmentId?: number,
  debouncedSearch: string = ""
) {
  const { data: studentData } = api.useQuery(
    "get",
    "/api/course/{course_id}/students",
    {
      params: {
        path: { course_id: courseId },
        query: {
          search: debouncedSearch,
          assignment_id: assignmentId,
        },
      },
    },
    { placeholderData: (prev) => prev }
  );

  return { studentData };
}
