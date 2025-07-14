import { api } from "@/utils/api";

export function useAssignmentDraft(assignmentId: number) {
  const {
    data: draftData,
    isLoading: draftDataLoading,
    isError: draftDataError,
  } = api.useQuery("get", "/api/assignment/{assignment_id}/draft", {
    params: {
      path: {
        assignment_id: assignmentId,
      },
    },
  });

  return {
    draftData,
    draftDataLoading,
    draftDataError,
  };
}
