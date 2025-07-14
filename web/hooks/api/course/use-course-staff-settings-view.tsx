import { api } from "@/utils/api";

export function useCourseStaffSettingsView(courseId: number) {
  const {
    data: settingsView,
    isLoading: settingsViewLoading,
    isError: settingsViewError,
  } = api.useQuery("get", "/api/course/{course_id}/staff-settings-view", {
    params: { path: { course_id: courseId } },
  });

  return {
    settingsView,
    settingsViewLoading,
    settingsViewError,
  };
}
