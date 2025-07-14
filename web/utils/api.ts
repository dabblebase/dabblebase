/** API client for type-safe interfacing with the backend. */

import createFetchClient from "openapi-fetch";
import createClient from "openapi-react-query";
import type { paths } from "../models/schema";
import { env } from "./env";

const protocol = env.MODE === "development" ? "http" : "https";

export const fetchClient = createFetchClient<paths>({
  baseUrl: `${protocol}://${env.HOST}`,
  credentials: "include",
});

export const api = createClient(fetchClient);
