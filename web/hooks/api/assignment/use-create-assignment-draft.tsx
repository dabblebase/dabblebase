import { api } from "@/utils/api";

export function useCreateAssignmentDraft() {
  const { mutate: createAssignmentDraft } = api.useMutation(
    "post",
    "/api/assignment/draft"
  );

  return { createAssignmentDraft };
}
