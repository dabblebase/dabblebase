import { api } from "@/utils/api";

export function useDashboard() {
  const {
    data: dashboardData,
    isLoading: dashboardLoading,
    error: dashboardError,
  } = api.useQuery("get", "/api/course/dashboard");

  const noCoursesFound =
    !dashboardError &&
    !dashboardLoading &&
    !dashboardData?.most_recent_staff_course_term &&
    !dashboardData?.most_recent_student_course_term;

  return {
    dashboardData,
    dashboardLoading,
    dashboardError,
    noCoursesFound,
  };
}
