import { api } from "@/utils/api";

export function useDeleteGroup() {
  const { mutate: deleteGroup } = api.useMutation(
    "delete",
    "/api/assignment/{assignment_id}/group/{group_id}"
  );

  return { deleteGroup };
}
