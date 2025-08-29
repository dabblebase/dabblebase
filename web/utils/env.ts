/** Helper to easily load env values with validation. */
import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

export const env = createEnv({
  server: {
    MODE: z.enum(["development", "production"]),
    HOST: z.string(),
    AUTH_MASTER_SECRET: z.string(),
  },
  client: {
    NEXT_PUBLIC_MODE: z.enum(["development", "production"]),
    NEXT_PUBLIC_HOST: z.string(),
    NEXT_PUBLIC_AUTH_MASTER_SECRET: z.string(),
  },
  runtimeEnv: {
    MODE: process.env.NEXT_PUBLIC_MODE,
    HOST: process.env.NEXT_PUBLIC_HOST,
    AUTH_MASTER_SECRET: process.env.NEXT_PUBLIC_AUTH_MASTER_SECRET,
    NEXT_PUBLIC_MODE: process.env.NEXT_PUBLIC_MODE,
    NEXT_PUBLIC_HOST: process.env.NEXT_PUBLIC_HOST,
    NEXT_PUBLIC_AUTH_MASTER_SECRET: process.env.NEXT_PUBLIC_AUTH_MASTER_SECRET,
  },
});
