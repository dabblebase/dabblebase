import { AuthenticatedRouteProps, protectRoute } from "@/utils/auth";
import { GetServerSidePropsContext } from "next";

export default function DashboardPage({ user }: AuthenticatedRouteProps) {
  return <p>Dashboard for user: {user.id}</p>;
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  return protectRoute(context, "/login");
}
