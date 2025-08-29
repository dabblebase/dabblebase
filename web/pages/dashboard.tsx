import DashboardLayout from "@/components/dashboard/dashboard-layout";
import { protectRoute } from "@/utils/auth";
import { GetServerSidePropsContext } from "next";
import ErrorMessage from "@/components/errors/error-message";
import { DashboardSection } from "@/components/dashboard/dashboard-section";
import { DashboardLoading } from "@/components/dashboard/dashboard-loading";
import { useDashboard } from "@/hooks/api/course/use-dashboard";
import JoinCourseDialog from "@/components/dashboard/join-course/join-course-dialog";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import JoinCourseNewStudent from "@/components/dashboard/join-course/join-course-new-student";
import CreateCourseDialog from "@/components/dashboard/create-course/create-course-dialog";

export default function DashboardPage() {
  const { dashboardData, dashboardLoading, dashboardError, noCoursesFound } =
    useDashboard();

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
      {!noCoursesFound && (
        <div className="flex flex-row gap-4 items-center">
          {!!dashboardData && dashboardData.is_instructor && (
            <CreateCourseDialog>
              <Button>
                <Plus />
                Create Course
              </Button>
            </CreateCourseDialog>
          )}
          <JoinCourseDialog>
            <Button variant="outline">
              <Plus />
              Join Course
            </Button>
          </JoinCourseDialog>
        </div>
      )}
      {!!dashboardData && noCoursesFound && (
        <JoinCourseNewStudent isInstructor={dashboardData.is_instructor} />
      )}
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
