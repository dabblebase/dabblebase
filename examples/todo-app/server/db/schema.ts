/**
 * This file defines the entire database schema - including all tables and relations.
 *
 * To configure the Dabblebase database using this schema as a guide, use the command:
 * ```
 * npx drizzle-kit push
 * ```
 *
 * @author Ajay Gandecha <agandecha@unc.edu>
 */

import { boolean, pgTable, serial, text, timestamp } from "drizzle-orm/pg-core";

/** Defines the `todos` database table. */
export const todosTable = pgTable("todos", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  completed: boolean("completed").notNull().default(false),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  userId: serial("user_id").notNull(),
});
