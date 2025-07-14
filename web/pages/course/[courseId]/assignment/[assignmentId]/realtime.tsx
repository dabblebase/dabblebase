import AssignmentLayout from "@/components/assignment/assignment-layout";
import { fetchClient } from "@/utils/api";
import { protectRoute } from "@/utils/auth";
import { GetServerSidePropsContext } from "next";

export default function AssignmentRealtimePage() {
  return (
    <div className="flex flex-col mx-auto w-full max-w-[1200px] px-4 gap-8 my-8">
      <h1 className="text-2xl font-semibold">Realtime</h1>
      <p className="text-accent-foreground/80">
        Realtime functionality for student projects coming soon!
      </p>
    </div>
  );
}

/**
 * Determine which page to show based on the assignment ID on the server side.
 */
export async function getServerSideProps(context: GetServerSidePropsContext) {
  const protectRouteResponse = protectRoute(context, "/login");
  // If the user is not authenticated, redirect to the login page
  if (protectRouteResponse && "redirect" in protectRouteResponse) {
    return protectRouteResponse;
  }
  // Otherwise, check for the assignment view using the API.
  const { assignmentId } = context.query;
  const id = assignmentId as unknown as number;

  // Call API to determine which assignment page to show.
  // Note: Cookies need to be expicitly passed since they are not automatically
  // included in the request header from the server-side context.
  const { data: viewData, error: viewError } = await fetchClient.GET(
    "/api/assignment/{assignment_id}/view",
    {
      params: { path: { assignment_id: id } },
      headers: {
        Cookie: context.req.headers.cookie || "",
      },
    }
  );

  // If there is a combination of the user role and assignment state that should
  // not be viewable, redirect to the assignments page.
  if (!viewData || viewError || viewData.should_redirect) {
    return {
      redirect: {
        destination: `/course/${context.query.courseId}/assignments`,
        permanent: false,
      },
    };
  }

  // If the user is a staff member, redirect to the staff page.
  if (
    viewData.role === "owner" ||
    viewData.role === "admin" ||
    viewData.role === "staff"
  ) {
    return {
      redirect: {
        destination: `/course/${context.query.courseId}/assignment/${assignmentId}`,
        permanent: false,
      },
    };
  }

  // If the view data is found, return it as props
  return {
    props: {
      viewData,
    },
  };
}

AssignmentRealtimePage.getLayout = function getLayout(page: React.ReactNode) {
  return <AssignmentLayout>{page}</AssignmentLayout>;
};
