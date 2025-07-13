import { api } from "@/utils/api";

export function useRenameGroup() {
  const { mutate: renameGroup } = api.useMutation(
    "put",
    "/api/assignment/{assignment_id}/group/{group_id}/rename"
  );

  return { renameGroup };
}
