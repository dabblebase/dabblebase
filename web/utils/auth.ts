/** Authentication-related utility functions. */

import { parse } from "cookie";
import jwt from "jsonwebtoken";
import { GetServerSidePropsContext } from "next";
import { env } from "./env";

/**
 * Protects a route by checking for a valid authentication token from within
 * the `getServerSideProps` function for a Next.js route.
 *
 * Usage:
 * ```
 * export default function Page({ user }) {...}
 *
 * export async function getServerSideProps(context: GetServerSidePropsContext) {
 *   return protectRoute(context, "/login");
 * }
 */

export const protectRoute = (
  context: GetServerSidePropsContext,
  redirect: string
) => {
  // Set up redirection response
  const redirectResponse = {
    redirect: {
      destination: redirect,
      permanent: false,
    },
  };

  // Parse the auth token from the request cookies
  const cookies = context.req.headers.cookie;
  const parsed = cookies ? parse(cookies) : {};
  const token = parsed["auth-token"];

  // If no token is found, redirect to the login page
  if (!token) {
    return redirectResponse;
  }

  // Verify the token
  try {
    const user = jwt.verify(token, env.AUTH_MASTER_SECRET);
    return { props: { user } };
  } catch {
    return redirectResponse;
  }
};

export type AuthenticatedRouteProps = { user: { id: number } };
