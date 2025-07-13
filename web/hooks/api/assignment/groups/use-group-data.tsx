import { api } from "@/utils/api";

export function useGroupData(assignmentId: number) {
  const { data: groupData, isError: groupDataError } = api.useQuery(
    "get",
    "/api/assignment/{assignment_id}/groups",
    {
      params: { path: { assignment_id: assignmentId } },
    }
  );

  return { groupData, groupDataError };
}
