import AssignmentLayout from "@/components/assignment/assignment-layout";
import { fetchClient } from "@/utils/api";
import { protectRoute } from "@/utils/auth";
import { GetServerSidePropsContext } from "next";
import type { components } from "@/models/schema";
import AssignmentDraftPage from "@/components/assignment/pages/draft/assignment-draft";
import { useRouter } from "next/router";

type Role = components["schemas"]["CourseMembershipRole"];
type AssignmentState = components["schemas"]["AssignmentState"];

type AssignmentViewData = {
  role: Role;
  assignment_state: AssignmentState;
};

export default function AssignmentPage({
  viewData,
}: {
  viewData: AssignmentViewData;
}) {
  const router = useRouter();
  const { courseId, assignmentId } = router.query;

  return (
    <>
      {viewData.role === "student" ? (
        <p>student view</p>
      ) : viewData.assignment_state === "draft" ? (
        <AssignmentDraftPage
          courseId={courseId as unknown as number}
          assignmentId={assignmentId as unknown as number}
        />
      ) : (
        <></>
      )}
    </>
  );
}

/**
 * Determine which assignment page to show based on the assignment ID on the server side.
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
  console.log(viewData, viewError);
  if (!viewData || viewError || viewData.should_redirect) {
    return {
      redirect: {
        destination: `/course/${context.query.courseId}/assignments`,
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

AssignmentPage.getLayout = function getLayout(page: React.ReactNode) {
  return <AssignmentLayout>{page}</AssignmentLayout>;
};
