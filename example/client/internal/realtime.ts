/** Types and functionality for the Dabblebase Realtime client */

import { Channel, Socket } from "phoenix";

type SocketConnection = {
  disconnect: () => void;
};

export type DbChangesSocketConnection = SocketConnection;
export type BroadcastsSocketConnection = SocketConnection & {
  broadcast: (payload: any) => void;
};

/** Client containing functionality to interact with Dabblebase Realtime */
export type DabblebaseRealtimeClient = {
  listenToDbChanges: (options: {
    onConnect?: () => void;
    onConnectError?: () => void;
    onDbChange?: (payload: unknown) => void;
  }) => DbChangesSocketConnection;
  listenForBroadcasts: (options: {
    channel: string;
    onConnect?: () => void;
    onConnectError?: () => void;
    onReceiveMessage?: (payload: unknown) => void;
  }) => BroadcastsSocketConnection;
  listenToPresenceChanges: (options: {
    onConnect?: () => void;
    onConnectError?: () => void;
    onReceivePresenceState?: (presenceState: unknown) => void;
  }) => SocketConnection;
};

/** Configuration for the Dabblebase Realtime client */
export type RealtimeClientConfiguration = {
  projectId: string;
  dabblebaseUrl?: string;
  authVerifyKey?: string;
  realtimeToken?: string;
  useSecureWebsocketConnection?: string;
};

/** Generates the Dabblebase Realtime client based on the provided configuration */
export function createRealtimeClient({
  projectId,
  dabblebaseUrl,
  authVerifyKey,
  realtimeToken,
  useSecureWebsocketConnection,
}: RealtimeClientConfiguration): DabblebaseRealtimeClient {
  // Internal function which creates the websocket connection for the route
  // dictated by the realtime client configuration
  const createWebsocket = (): Socket => {
    const protocol = useSecureWebsocketConnection ? "wss" : "ws";
    return new Socket(`${protocol}://${dabblebaseUrl}/ws`, {
      params: {
        realtime_token: realtimeToken,
        auth_token: "...",
      },
    });
  };

  return {
    listenToDbChanges: ({ onConnect, onConnectError, onDbChange }) => {
      const socket = createWebsocket();
      socket.connect();
      const channel = socket.channel(`db:${projectId}`);
      channel
        .join()
        .receive("ok", (_) => onConnect?.())
        .receive("error", (_) => {
          onConnectError?.();
          throw new Error(
            "❌ (dabblebase): Unable to connect to the db changes websocket channel."
          );
        });
      channel.on("pg_change", (payload) => {
        onDbChange?.(payload);
      });
      return {
        disconnect: () => {
          channel.leave();
          socket.disconnect();
        },
      };
    },
    listenForBroadcasts: ({
      channel: channelName,
      onConnect,
      onConnectError,
      onReceiveMessage,
    }) => {
      const socket = createWebsocket();
      socket.connect();
      const channel = socket.channel(`broadcast:${projectId}:${channelName}`);
      channel
        .join()
        .receive("ok", (_) => onConnect?.())
        .receive("error", (_) => {
          onConnectError?.();
          throw new Error(
            `❌ (dabblebase): Unable to connect to the broadcast websocket channel ${channelName}.`
          );
        });
      channel.on("message", (payload) => {
        onReceiveMessage?.(payload);
      });
      return {
        broadcast: (payload) => {
          channel.push("message", payload);
        },
        disconnect: () => {
          channel.leave();
          socket.disconnect();
        },
      };
    },
    listenToPresenceChanges: ({
      onConnect,
      onConnectError,
      onReceivePresenceState,
    }) => {
      const socket = createWebsocket();
      socket.connect();
      const channel = socket.channel(`presence:${projectId}`);
      channel
        .join()
        .receive("ok", (_) => onConnect?.())
        .receive("error", (_) => {
          onConnectError?.();
          throw new Error(
            `❌ (dabblebase): Unable to connect to the presence websocket channel.`
          );
        });
      channel.on("presence_state", (payload) => {
        onReceivePresenceState?.(payload);
      });
      return {
        disconnect: () => {
          channel.leave();
          socket.disconnect();
        },
      };
    },
  };
}
