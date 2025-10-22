import { api } from "@/utils/api";

export function useProjectStorage(assignmentId: number) {
  const {
    data: storageData,
    isLoading: isStorageLoading,
    error: storageError,
  } = api.useQuery(
    "get",
    "/api/assignment/{assignment_id}/student-project/storage",
    {
      params: {
        path: {
          assignment_id: assignmentId,
        },
      },
    }
  );

  return {
    storageData,
    isStorageLoading,
    storageError,
  };
}
