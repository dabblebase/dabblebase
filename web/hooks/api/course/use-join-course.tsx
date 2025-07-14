import { api } from "@/utils/api";

export function useJoinCourse() {
  const { mutate: joinCourse } = api.useMutation(
    "post",
    "/api/course/join-with-invite-code"
  );
  return {
    joinCourse,
  };
}
