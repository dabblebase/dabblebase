/** API client for type-safe interfacing with the backend. */

import createFetchClient from "openapi-fetch";
import createClient from "openapi-react-query";
import type { paths } from "../models/schema";

// TODO: Improve this process here.
const url =
  process.env.NODE_ENV === "development"
    ? "http://localhost:8000"
    : "https://www.dabblebase.dev";

export const fetchClient = createFetchClient<paths>({
  baseUrl: url,
  credentials: "include",
});

export const api = createClient(fetchClient);
