import { api } from "@/utils/api";

export function useCreateCourse() {
  const { mutate: createCourse } = api.useMutation("post", "/api/course/");

  return { createCourse };
}
