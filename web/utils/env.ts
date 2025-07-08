/** Helper to easily load env values with validation. */

import { z } from "zod";

const EnvType = z.object({
  MODE: z.enum(["development", "production"]).default("development"),
  AUTH_MASTER_SECRET: z.string().default("REPLACE_ME"),
});

export const env = EnvType.parse(process.env);
