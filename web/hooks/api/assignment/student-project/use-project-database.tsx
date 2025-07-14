import { api } from "@/utils/api";

export function useProjectDatabase(assignmentId: number) {
  const {
    data: databaseData,
    isLoading: isDatabaseLoading,
    error: databaseError,
  } = api.useQuery(
    "get",
    "/api/assignment/{assignment_id}/student-project/database",
    {
      params: {
        path: {
          assignment_id: assignmentId,
        },
      },
    }
  );

  return {
    databaseData,
    isDatabaseLoading,
    databaseError,
  };
}
