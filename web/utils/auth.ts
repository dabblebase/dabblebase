/** Authentication-related utility functions. */

import { parse } from "cookie";
import jwt from "jsonwebtoken";
import { GetServerSidePropsContext } from "next";
import { env } from "./env";
import { api } from "./api";
import { useRouter } from "next/router";

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
    const user = jwt.verify(token, env.AUTH_MASTER_SECRET) as { id: number };
    return {
      props: {
        auth: {
          userId: user.id,
          isAuthenticated: true,
        },
      },
    };
  } catch {
    return redirectResponse;
  }
};

export const getAuthState = (context: GetServerSidePropsContext): AuthState => {
  const cookies = context.req.headers.cookie;
  const parsed = cookies ? parse(cookies) : {};
  const token = parsed["auth-token"];

  if (!token) {
    return { userId: null, isAuthenticated: false };
  }

  try {
    const user = jwt.verify(token, env.AUTH_MASTER_SECRET) as { id: number };
    return {
      userId: user.id,
      isAuthenticated: true,
    };
  } catch {
    return { userId: null, isAuthenticated: false };
  }
};

export type AuthState = {
  userId: number | null;
  isAuthenticated: boolean;
};

/** Type including the props for an authenticated route. */
export type AuthenticatedRouteProps = {
  auth: AuthState;
};

export const useLogOut = () => {
  const router = useRouter();
  const { mutate } = api.useMutation("post", "/auth/logout", {
    onSuccess: () => {
      router.push("/");
    },
  });
  const logOut = () => mutate({});
  return { logOut };
};
