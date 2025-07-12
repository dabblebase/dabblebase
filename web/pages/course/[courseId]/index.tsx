import CourseLayout from "@/components/course/course-layout";
import { GetServerSidePropsContext } from "next";

export default function CoursePage() {
  return <></>;
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  return {
    redirect: {
      destination: `/course/${context.params?.courseId}/assignments`,
      permanent: false,
    },
  };
}

CoursePage.getLayout = function getLayout(page: React.ReactNode) {
  return <CourseLayout>{page}</CourseLayout>;
};
