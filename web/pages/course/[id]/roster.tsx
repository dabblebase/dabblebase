import CourseLayout from "@/components/course/course-layout";
import { protectRoute } from "@/utils/auth";
import { GetServerSidePropsContext } from "next";

export default function CourseRosterPage() {
  return (
    <div className="flex flex-col mx-auto w-full max-w-[1200px] px-4 gap-8 my-8">
      <h1 className="text-2xl font-semibold">Roster</h1>
      <p>Coming soon!</p>
    </div>
  );
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  return protectRoute(context, "/login");
}

CourseRosterPage.getLayout = function getLayout(page: React.ReactNode) {
  return <CourseLayout>{page}</CourseLayout>;
};
