/** Helper to easily load env values with validation. */

import { z } from "zod";

const EnvType = z.object({
  MODE: z.enum(["development", "production"]).default("development"),
  HOST: z.string().default("localhost:8000"),
});

export const env = EnvType.parse(process.env);
