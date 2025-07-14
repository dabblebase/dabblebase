import { fetchClient } from "@/utils/api";
import { protectRoute } from "@/utils/auth";
import { GetServerSidePropsContext } from "next";
import CourseLayout from "@/components/course/course-layout";
import CourseStaffSettings from "@/components/course/settings/views/course-staff-settings";
import { useRouter } from "next/router";

export default function CourseSettingsPage({
  isStudent,
}: {
  isStudent: boolean;
}) {
  const router = useRouter();
  const { courseId } = router.query;
  return (
    <>
      {isStudent ? (
        <p>Student view...</p>
      ) : (
        <CourseStaffSettings courseId={courseId as unknown as number} />
      )}
    </>
  );
}

/**
 * Determine which settings page to show based on the user's role in the course on the server side.
 */
export async function getServerSideProps(context: GetServerSidePropsContext) {
  const protectRouteResponse = protectRoute(context, "/login");
  // If the user is not authenticated, redirect to the login page
  if (protectRouteResponse && "redirect" in protectRouteResponse) {
    return protectRouteResponse;
  }
  // Otherwise, check for the course role of the student.
  const { courseId } = context.query;
  const id = courseId as unknown as number;

  // Call API to determine which page to show.
  // Note: Cookies need to be expicitly passed since they are not automatically
  // included in the request header from the server-side context.
  const { data: roleData, error: roleError } = await fetchClient.GET(
    "/api/course/{course_id}/role",
    {
      params: { path: { course_id: id } },
      headers: {
        Cookie: context.req.headers.cookie || "",
      },
    }
  );

  // If the user has no role, redirect away.
  if (!roleData || roleError || !roleData.role) {
    return {
      redirect: {
        destination: `/dashboard`,
        permanent: false,
      },
    };
  }
  // Based on the role, determine if the user is a student or staff.
  const isStudent = roleData.role === "student";

  // Pass the result as props
  return {
    props: {
      isStudent,
    },
  };
}

CourseSettingsPage.getLayout = function getLayout(page: React.ReactNode) {
  return <CourseLayout>{page}</CourseLayout>;
};
