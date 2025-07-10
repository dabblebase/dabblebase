import CourseLayout from "@/components/course/course-layout";
import { protectRoute } from "@/utils/auth";
import { GetServerSidePropsContext } from "next";
import { useRouter } from "next/router";

export default function CourseAssignmentsPage() {
  const router = useRouter();

  const { id } = router.query;

  return (
    <div className="flex flex-col mx-auto w-full max-w-[1200px] px-4 gap-8 my-8">
      <h1 className="text-2xl font-semibold">Assignments</h1>
      <p>This is the course page for course with ID: {id}</p>
      {/* Additional course content can be added here */}
    </div>
  );
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  return protectRoute(context, "/login");
}

CourseAssignmentsPage.getLayout = function getLayout(page: React.ReactNode) {
  return <CourseLayout>{page}</CourseLayout>;
};
