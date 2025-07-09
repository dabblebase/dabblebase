import DashboardLayout from "@/components/dashboard/dashboard-layout";
import { api } from "@/utils/api";
import { protectRoute } from "@/utils/auth";
import { GetServerSidePropsContext } from "next";
import ErrorMessage from "@/components/errors/error-message";
import { DashboardSection } from "@/components/dashboard/dashboard-section";
import { DashboardLoading } from "@/components/dashboard/dashboard-loading";

export default function DashboardPage() {
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

  return (
    <div className="flex flex-col mx-auto w-full max-w-[1200px] px-4 gap-8 my-8">
      <DashboardSection
        title="Staff Courses"
        mostRecentTerm={dashboardData?.most_recent_staff_course_term}
        otherTerms={dashboardData?.other_staff_course_terms ?? []}
        courses={dashboardData?.staff_courses ?? {}}
      />
      <DashboardSection
        title="Student Courses"
        mostRecentTerm={dashboardData?.most_recent_student_course_term}
        otherTerms={dashboardData?.other_student_course_terms ?? []}
        courses={dashboardData?.student_courses ?? {}}
      />
      {noCoursesFound && <p className="text-lg">No courses found.</p>}
      {dashboardLoading && <DashboardLoading title="Student Courses" />}
      {dashboardError && <ErrorMessage resource="dashboard" />}
    </div>
  );
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  return protectRoute(context, "/login");
}

DashboardPage.getLayout = function getLayout(page: React.ReactNode) {
  return <DashboardLayout>{page}</DashboardLayout>;
};
