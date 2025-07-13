import { api } from "@/utils/api";

export function useCreateGroup() {
  const { mutate: createGroup } = api.useMutation(
    "post",
    "/api/assignment/{assignment_id}/group"
  );

  return { createGroup };
}
