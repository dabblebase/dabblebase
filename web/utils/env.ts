/** Helper to easily load env values with validation. */
import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

export const env = createEnv({
  server: {
    MODE: z.enum(["development", "production"]).default("production"),
    HOST: z.string().default("www.dabblebase.com"),
    AUTH_MASTER_SECRET: z
      .string()
      .default("default-secret-change-in-production"),
  },
  client: {
    NEXT_PUBLIC_MODE: z
      .enum(["development", "production"])
      .default("production"),
    NEXT_PUBLIC_HOST: z.string().default("www.dabblebase.com"),
  },
  runtimeEnv: {
    // Server variables (not exposed to client)
    MODE: process.env.MODE,
    HOST: process.env.HOST,
    AUTH_MASTER_SECRET: process.env.AUTH_MASTER_SECRET,
    // Client variables (exposed to client)
    NEXT_PUBLIC_MODE: process.env.NEXT_PUBLIC_MODE,
    NEXT_PUBLIC_HOST: process.env.NEXT_PUBLIC_HOST,
  },
  skipValidation: !!process.env.SKIP_ENV_VALIDATION,
});
