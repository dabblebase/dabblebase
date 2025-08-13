import { api } from "@/utils/api";

export function useProjectRealtime(assignmentId: number) {
  const {
    data: realtimeData,
    isLoading: isRealtimeLoading,
    error: realtimeError,
  } = api.useQuery(
    "get",
    "/api/assignment/{assignment_id}/student-project/realtime",
    {
      params: {
        path: {
          assignment_id: assignmentId,
        },
      },
    }
  );

  return {
    realtimeData,
    isRealtimeLoading,
    realtimeError,
  };
}
