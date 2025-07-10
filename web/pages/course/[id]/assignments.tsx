import { AssignmentsList } from "@/components/assignment/assignments-list";
import { AssignmentsLoading } from "@/components/assignment/assignments-loading";
import CourseLayout from "@/components/course/course-layout";
import ErrorMessage from "@/components/errors/error-message";
import { api } from "@/utils/api";
import { protectRoute } from "@/utils/auth";
import { GetServerSidePropsContext } from "next";
import { useRouter } from "next/router";

export default function CourseAssignmentsPage() {
  const router = useRouter();

  const { id } = router.query;

  const {
    data: assignmentsData,
    isLoading: assignmentsLoading,
    error: assignmentsError,
  } = api.useQuery("get", "/api/course/{course_id}/assignments", {
    params: { path: { course_id: id as unknown as number } },
  });

  const noAssignmentsFound =
    !!assignmentsData && assignmentsData.assignments.length === 0;

  return (
    <div className="flex flex-col mx-auto w-full max-w-[1200px] px-4 gap-8 my-8">
      <h1 className="text-2xl font-semibold">Assignments</h1>
      {!!assignmentsData && (
        <AssignmentsList
          assignments={assignmentsData.assignments}
          isStaff={assignmentsData.is_staff}
        />
      )}
      {noAssignmentsFound && <p className="text-lg">No assignments found.</p>}
      {assignmentsLoading && <AssignmentsLoading />}
      {assignmentsError && <ErrorMessage resource="assignments" />}
    </div>
  );
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  return protectRoute(context, "/login");
}

CourseAssignmentsPage.getLayout = function getLayout(page: React.ReactNode) {
  return <CourseLayout>{page}</CourseLayout>;
};
