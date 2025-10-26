import { z } from "zod";

/** Defines the schema for a todo item. */
export const TodoItem = z.object({
  id: z.number(),
  title: z.string(),
  completed: z.boolean(),
});
