/**
 * tRPC APIs that contains all of the functionality for creating,
 * reading, updating, and deleting data in our database relating to
 * todo items.
 *
 * @author Ajay Gandecha <agandecha@unc.edu>
 */

import { TodoItem } from "@/server/models/todos";
import { createTRPCRouter, protectedProcedure } from "../trpc";
import { db } from "@/server/db";
import { asc, eq } from "drizzle-orm";
import { todosTable } from "@/server/db/schema";
import { TRPCError } from "@trpc/server";
import z from "zod";

const getTodoItems = protectedProcedure
  .output(TodoItem.array())
  .query(async ({ ctx }) => {
    const { subject } = ctx;

    if (!subject) {
      throw new TRPCError({
        code: "UNAUTHORIZED",
        message: "You must be logged in to view todos.",
      });
    }

    const todos = await db.query.todosTable.findMany({
      orderBy: (todo) => asc(todo.createdAt),
      where: eq(todosTable.userId, subject!.id),
    });

    return TodoItem.array().parse(todos);
  });

const createTodoItem = protectedProcedure
  .input(
    z.object({
      title: z.string(),
    })
  )
  .mutation(async ({ ctx, input }) => {
    const { subject } = ctx;

    if (!subject) {
      throw new TRPCError({
        code: "UNAUTHORIZED",
        message: "You must be logged in to create todos.",
      });
    }

    const todo = await db
      .insert(todosTable)
      .values({
        title: input.title,
        userId: subject.id,
      })
      .returning();

    return TodoItem.parse(todo[0]);
  });

const toggleTodoItem = protectedProcedure
  .input(
    z.object({
      id: z.number(),
    })
  )
  .mutation(async ({ ctx, input }) => {
    const { subject } = ctx;

    if (!subject) {
      throw new TRPCError({
        code: "UNAUTHORIZED",
        message: "You must be logged in to toggle todos.",
      });
    }

    const todoItem = await db.query.todosTable.findFirst({
      where: eq(todosTable.id, input.id),
    });

    if (!todoItem) {
      throw new TRPCError({
        code: "NOT_FOUND",
        message: `Todo item with id ${input.id} not found.`,
      });
    }

    if (todoItem.userId !== subject.id) {
      throw new TRPCError({
        code: "FORBIDDEN",
        message: "You do not have permission to toggle this todo item.",
      });
    }

    const todo = await db
      .update(todosTable)
      .set({
        completed: !todoItem.completed,
      })
      .where(eq(todosTable.id, input.id))
      .returning();
    return TodoItem.parse(todo[0]);
  });

const updateTodoItem = protectedProcedure
  .input(
    z.object({
      id: z.number(),
      title: z.string().min(1, "Title is required"),
    })
  )
  .mutation(async ({ ctx, input }) => {
    const { subject } = ctx;

    if (!subject) {
      throw new TRPCError({
        code: "UNAUTHORIZED",
        message: "You must be logged in to update todos.",
      });
    }

    const todoItem = await db.query.todosTable.findFirst({
      where: eq(todosTable.id, input.id),
    });

    if (!todoItem) {
      throw new TRPCError({
        code: "NOT_FOUND",
        message: `Todo item with id ${input.id} not found.`,
      });
    }

    if (todoItem.userId !== subject.id) {
      throw new TRPCError({
        code: "FORBIDDEN",
        message: "You do not have permission to update this todo item.",
      });
    }

    const todo = await db
      .update(todosTable)
      .set({
        title: input.title,
      })
      .where(eq(todosTable.id, input.id))
      .returning();

    return TodoItem.parse(todo[0]);
  });

const deleteTodoItem = protectedProcedure
  .input(
    z.object({
      id: z.number(),
    })
  )
  .mutation(async ({ ctx, input }) => {
    const { subject } = ctx;

    if (!subject) {
      throw new TRPCError({
        code: "UNAUTHORIZED",
        message: "You must be logged in to delete todos.",
      });
    }

    const todoItem = await db.query.todosTable.findFirst({
      where: eq(todosTable.id, input.id),
    });

    if (!todoItem) {
      throw new TRPCError({
        code: "NOT_FOUND",
        message: `Todo item with id ${input.id} not found.`,
      });
    }

    if (todoItem.userId !== subject.id) {
      throw new TRPCError({
        code: "FORBIDDEN",
        message: "You do not have permission to delete this todo item.",
      });
    }

    await db.delete(todosTable).where(eq(todosTable.id, input.id));
  });

/**
 * Router for all todo-related APIs.
 */
export const todosRouter = createTRPCRouter({
  createTodoItem: createTodoItem,
  getTodoItems: getTodoItems,
  updateTodoItem: updateTodoItem,
  toggleTodoItem: toggleTodoItem,
  deleteTodoItem: deleteTodoItem,
});
