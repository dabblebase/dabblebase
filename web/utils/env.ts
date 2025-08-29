/** Helper to easily load env values with validation. */

import { z } from "zod";

const EnvType = z.object({
  MODE: z.enum(["development", "production"]),
  HOST: z.string(),
  AUTH_MASTER_SECRET: z.string(),
});

// For client-side, we need to access the environment variables differently
// In Next.js, NEXT_PUBLIC_ variables are available on both client and server
const clientEnv = {
  MODE: process.env.NEXT_PUBLIC_MODE,
  HOST: process.env.NEXT_PUBLIC_HOST,
  AUTH_MASTER_SECRET: process.env.NEXT_PUBLIC_AUTH_MASTER_SECRET,
};

export const env = EnvType.parse(clientEnv);
