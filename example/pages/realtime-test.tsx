import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { dabblebase } from "@/utils/dabblebase/client";
import type {
  PresenceState,
  PresenceSocketConnection,
  BroadcastsSocketConnection,
} from "@/client/internal/realtime";

export default function RealtimeTestPage() {
  // Presence state
  const [presenceState, setPresenceState] = useState<PresenceState>({});
  const [presenceConnection, setPresenceConnection] =
    useState<PresenceSocketConnection | null>(null);

  // Broadcast state
  const [broadcastMessages, setBroadcastMessages] = useState<unknown[]>([]);
  const [broadcastConnection, setBroadcastConnection] =
    useState<BroadcastsSocketConnection | null>(null);
  const [broadcastMessage, setBroadcastMessage] = useState("");

  // Connection states
  const [connections, setConnections] = useState({
    presence: false,
    broadcast: false,
  });

  // Presence functionality
  const connectToPresence = async () => {
    try {
      const connection = dabblebase.realtime.listenToPresenceChanges({
        onConnect: () => {
          console.log("✅ Connected to presence");
          setConnections((prev) => ({ ...prev, presence: true }));
        },
        onConnectError: (error) => {
          console.error("❌ Presence connection error:", error);
          setConnections((prev) => ({ ...prev, presence: false }));
        },
        onReceivePresenceState: (state) => {
          console.log("👥 Presence state:", state);
          setPresenceState(state);
        },
        onPresenceJoin: (userId, presence) => {
          console.log(`👋 ${userId} joined at ${presence.online_at}`);
        },
        onPresenceLeave: (userId) => {
          console.log(`👋 ${userId} left`);
        },
      });
      setPresenceConnection(connection);
    } catch (error) {
      console.error("Failed to connect to presence:", error);
    }
  };

  const disconnectFromPresence = () => {
    if (presenceConnection) {
      presenceConnection.disconnect();
      setPresenceConnection(null);
      setConnections((prev) => ({ ...prev, presence: false }));
      setPresenceState({});
    }
  };

  // Broadcast functionality
  const connectToBroadcast = async () => {
    try {
      const connection = dabblebase.realtime.listenForBroadcasts({
        channel: "chat",
        onConnect: () => {
          console.log("✅ Connected to broadcast channel 'chat'");
          setConnections((prev) => ({ ...prev, broadcast: true }));
        },
        onConnectError: (error) => {
          console.error("❌ Broadcast connection error:", error);
          setConnections((prev) => ({ ...prev, broadcast: false }));
        },
        onReceiveMessage: (message) => {
          console.log("📢 Broadcast message:", message);
          setBroadcastMessages((prev) => [message, ...prev.slice(0, 9)]); // Keep last 10 messages
        },
      });
      setBroadcastConnection(connection);
    } catch (error) {
      console.error("Failed to connect to broadcast:", error);
    }
  };

  const disconnectFromBroadcast = () => {
    if (broadcastConnection) {
      broadcastConnection.disconnect();
      setBroadcastConnection(null);
      setConnections((prev) => ({ ...prev, broadcast: false }));
      setBroadcastMessages([]);
    }
  };

  const sendBroadcastMessage = () => {
    if (broadcastConnection && broadcastMessage.trim()) {
      broadcastConnection.broadcast({
        text: broadcastMessage.trim(),
        timestamp: new Date().toISOString(),
        sender: "user_1", // In a real app, this would be the current user ID
      });
      setBroadcastMessage("");
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      presenceConnection?.disconnect();
      broadcastConnection?.disconnect();
    };
  }, [presenceConnection, broadcastConnection]);

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">Dabblebase Realtime Test</h1>
      <p className="text-gray-600 mb-6">
        Test broadcast messaging and presence tracking. Open multiple browser
        tabs to see real-time features in action!
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Presence Section */}
        <div className="bg-white border rounded-lg p-4">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            👥 Presence
            <span
              className={`w-3 h-3 rounded-full ${
                connections.presence ? "bg-green-500" : "bg-red-500"
              }`}
            ></span>
          </h2>

          <div className="space-y-2 mb-4">
            {!connections.presence ? (
              <Button onClick={connectToPresence} className="w-full">
                Connect to Presence
              </Button>
            ) : (
              <Button
                onClick={disconnectFromPresence}
                variant="destructive"
                className="w-full"
              >
                Disconnect
              </Button>
            )}
          </div>

          <div className="space-y-2 max-h-60 overflow-y-auto">
            {Object.keys(presenceState).length === 0 ? (
              <p className="text-gray-500 text-sm">No users online...</p>
            ) : (
              Object.entries(presenceState).map(([userId, { metas }]) => (
                <div key={userId} className="bg-gray-50 p-2 rounded text-sm">
                  <div className="font-semibold text-green-600">
                    👤 {userId}
                  </div>
                  {metas.map((meta, index) => (
                    <div key={index} className="text-gray-600 text-xs">
                      Online since: {meta.online_at}
                    </div>
                  ))}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Broadcast Section */}
        <div className="bg-white border rounded-lg p-4">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            📢 Broadcast Chat
            <span
              className={`w-3 h-3 rounded-full ${
                connections.broadcast ? "bg-green-500" : "bg-red-500"
              }`}
            ></span>
          </h2>

          <div className="space-y-2 mb-4">
            {!connections.broadcast ? (
              <Button onClick={connectToBroadcast} className="w-full">
                Connect to Chat
              </Button>
            ) : (
              <Button
                onClick={disconnectFromBroadcast}
                variant="destructive"
                className="w-full"
              >
                Disconnect
              </Button>
            )}
          </div>

          {connections.broadcast && (
            <div className="space-y-2 mb-4">
              <Input
                type="text"
                placeholder="Type a message..."
                value={broadcastMessage}
                onChange={(e) => setBroadcastMessage(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && sendBroadcastMessage()}
              />
              <Button
                onClick={sendBroadcastMessage}
                disabled={!broadcastMessage.trim()}
                className="w-full"
              >
                Send Message
              </Button>
            </div>
          )}

          <div className="space-y-2 max-h-60 overflow-y-auto">
            {broadcastMessages.length === 0 ? (
              <p className="text-gray-500 text-sm">No messages yet...</p>
            ) : (
              broadcastMessages.map((message, index) => (
                <div key={index} className="bg-gray-50 p-2 rounded text-sm">
                  <div className="text-gray-800">
                    {JSON.stringify(message, null, 2)}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="mt-8 bg-blue-50 border border-blue-200 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-2 text-blue-900">
          Instructions:
        </h3>
        <ul className="list-disc list-inside space-y-1 text-sm text-blue-800">
          <li>
            <strong>Presence:</strong> Connect to see who else is online in the
            project. Open multiple tabs to simulate different users.
          </li>
          <li>
            <strong>Broadcast Chat:</strong> Connect to send and receive
            messages in the &quot;chat&quot; channel in real-time.
          </li>
          <li>
            Open multiple browser tabs or windows to test the realtime features
            between different &quot;users&quot;.
          </li>
          <li>
            Check the browser console for detailed connection logs and debugging
            information.
          </li>
        </ul>
      </div>
    </div>
  );
}
