import { AssignmentsList } from "@/components/assignment/assignments-list";
import { AssignmentsLoading } from "@/components/assignment/assignments-loading";
import CreateAssignmentDialog from "@/components/assignment/create-assignment-dialog";
import CourseLayout from "@/components/course/course-layout";
import ErrorMessage from "@/components/errors/error-message";
import { Button } from "@/components/ui/button";
import { api } from "@/utils/api";
import { protectRoute } from "@/utils/auth";
import { Plus } from "lucide-react";
import { GetServerSidePropsContext } from "next";
import { useRouter } from "next/router";

export default function CourseAssignmentsPage() {
  const router = useRouter();

  const { courseId } = router.query;
  const id = courseId as unknown as number;

  const {
    data: assignmentsData,
    isLoading: assignmentsLoading,
    error: assignmentsError,
  } = api.useQuery("get", "/api/course/{course_id}/assignments", {
    params: { path: { course_id: id } },
  });

  const { data: courseRoleData } = api.useQuery(
    "get",
    "/api/course/{course_id}/role",
    {
      params: { path: { course_id: id } },
    }
  );

  const noAssignmentsFound =
    !!assignmentsData && assignmentsData.assignments.length === 0;

  return (
    <div className="flex flex-col mx-auto w-full max-w-[1200px] px-4 gap-8 my-8">
      <div className="flex flex-row w-full justify-between">
        <h1 className="text-2xl font-semibold">Assignments</h1>
        {!!courseRoleData && courseRoleData.can_modify_assignments && (
          <CreateAssignmentDialog courseId={id}>
            <Button>
              <Plus />
              New Assignment
            </Button>
          </CreateAssignmentDialog>
        )}
      </div>

      {!!assignmentsData && (
        <AssignmentsList
          courseId={id}
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
