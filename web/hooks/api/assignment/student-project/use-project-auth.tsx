import { api } from "@/utils/api";

export function useProjectAuth(assignmentId: number) {
  const {
    data: authData,
    isLoading: isAuthLoading,
    error: authError,
  } = api.useQuery(
    "get",
    "/api/assignment/{assignment_id}/student-project/auth",
    {
      params: {
        path: {
          assignment_id: assignmentId,
        },
      },
    }
  );

  return {
    authData,
    isAuthLoading,
    authError,
  };
}
