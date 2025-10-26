/**
 * Configuration for the server-side tRPC API, including the primary API router.
 * Configuration of the server-side tRPC API.
 *
 * @author Ajay Gandecha <agandecha@unc.edu>
 */

import { createCallerFactory, createTRPCRouter } from "@/server/api/trpc";
import { todosRouter } from "@/server/api/routers/todos";

/** Primary router for the API server. */
export const appRouter = createTRPCRouter({
  todos: todosRouter,
});

export type AppRouter = typeof appRouter;
export const createCaller = createCallerFactory(appRouter);
