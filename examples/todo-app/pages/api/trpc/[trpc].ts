/**
 * This routing handler exposes an API endpoing that the client-side tRPC functions use to
 * communicate with the server-side tRPC procedures. Do not modify this file.
 *
 * @author Ajay Gandecha <agandecha@unc.edu>
 */

import { createNextApiHandler } from "@trpc/server/adapters/next";
import { appRouter } from "@/server/api/root";
import { createTRPCContext } from "@/server/api/trpc";

export default createNextApiHandler({
  router: appRouter,
  createContext: createTRPCContext,
  onError:
    process.env.NODE_ENV === "development"
      ? ({ path, error }) => {
          console.error(
            `❌ tRPC failed on ${path ?? "<no-path>"}: ${error.message}`
          );
        }
      : undefined,
});
