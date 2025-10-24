/** Defines the Dabblebase client */

import { createAuthClient, DabblebaseAuthClient } from "./internal/auth";
import {
  createStorageClient,
  DabblebaseStorageClient,
} from "./internal/storage";

/** Configuration for the Dabblebase client */
export type ClientConfiguration = {
  projectId: string;
  projectUrl: string;
  dabblebaseUrl?: string;
  authVerifyKey?: string;
  projectVerifyKey?: string;
  realtimeToken?: string;
  useSecureWebsocketConnection?: boolean;
};

/** The Dabblebase client used to interface with core Dabblebase features */
export interface DabblebaseClient {
  /** Authentication client used to interface with Dabblebase Auth */
  auth: DabblebaseAuthClient;
  /** Storage client used to interface with Dabblebase Storage */
  storage: DabblebaseStorageClient;
}

/**
 * Generates the Dabblebase client based on the provided configuration
 *
 * @params config - Dabblebase client configuration.
 *  - dabblebaseUrl: If you are using a different deployment of Dabblebase than
 *    the official one at `www.dabblebase.dev`, provide another URL.
 * - authVerifyKey: Used by the Dabblebase Auth client to verify that a user
 *    has signed in legitimately and correctly.
 * - realtimeToken: Used to authenticate with Dabblebase Realtime.
 */
export function createClient({
  projectId,
  projectUrl,
  dabblebaseUrl = "www.dabblebase.dev",
  authVerifyKey,
  projectVerifyKey,
  realtimeToken,
  useSecureWebsocketConnection = true,
}: ClientConfiguration) {
  return {
    auth: createAuthClient({
      projectId,
      projectUrl,
      dabblebaseUrl,
      authVerifyKey,
    }),
    storage: createStorageClient({
      projectId,
      dabblebaseUrl,
      projectVerifyKey: projectVerifyKey,
    }),
  } as DabblebaseClient;
}
