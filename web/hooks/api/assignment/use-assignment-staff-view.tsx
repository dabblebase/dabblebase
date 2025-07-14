import { api } from "@/utils/api";

export function useAssignmentStaffView(assignmentId: number) {
  const {
    data: staffViewData,
    isLoading: staffViewLoading,
    isError: staffViewError,
    refetch: refetchStaffViewData,
  } = api.useQuery("get", "/api/assignment/{assignment_id}/staff-view", {
    params: {
      path: {
        assignment_id: assignmentId,
      },
    },
  });

  const { data: individualProjectData, isError: individualProjectError } =
    api.useQuery(
      "get",
      "/api/assignment/{assignment_id}/student-projects",
      {
        params: {
          path: {
            assignment_id: assignmentId,
          },
        },
      },
      {
        enabled: !!staffViewData && staffViewData.is_group === false,
      }
    );

  const { data: groupProjectData, isError: groupProjectError } = api.useQuery(
    "get",
    "/api/assignment/{assignment_id}/group-projects",
    {
      params: {
        path: {
          assignment_id: assignmentId,
        },
      },
    },
    {
      enabled: !!staffViewData && staffViewData.is_group === true,
    }
  );

  return {
    staffViewData,
    staffViewLoading,
    staffViewError,
    refetchStaffViewData,
    individualProjectData,
    individualProjectError,
    groupProjectData,
    groupProjectError,
  };
}
