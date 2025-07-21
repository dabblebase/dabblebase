import { Socket } from "phoenix";
import { useEffect } from "react";

export default function TestPage() {
  useEffect(() => {
    // Create a socket connection
    const socket = new Socket("ws://localhost:8000/ws", {
      params: {
        realtime_token:
          "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0X2lkIjoxfQ.haxqz7Ph5cU4t7DiB7C8PQhfyGd-hFPiSoSKduAYlVFSpB1Im_jd1gZ6v0Uwg5G9GMACNf7yFciuAw4oH16vB2j8g86ndbDl8eVYo05KjwfACZLgfbXEFHfO1SnKEOenord4qnzP5c3nxsFz7A7ABFB-HFC5cfc6Sr8RZ8ZumeSG60WmxeEBNTtBPv9CSf8tWeVODljgygJF_4oKag8XPW9A0zODpaeY6uFtaijIpbUoZpW9KKXMuugiV7YnogBpTsIjtXbKNIeMwJLjSjm97nQylrpOz4cTVsoTqMGPHyev2fnQL76o1PD3J6nikQM-l06cHta2dZwPH97Sz1ERcQ",
      },
    });

    socket.connect();

    // Join the channel
    const channel = socket.channel("db:1", {});

    channel
      .join()
      .receive("ok", (resp) => {
        console.log("✅ Joined successfully", resp);
      })
      .receive("error", (resp) => {
        console.error("❌ Unable to join", resp);
      });

    // Listen for pg_change events
    channel.on("pg_change", (payload) => {
      console.log("📣 Postgres change event:", payload);
    });
  }, []);

  return (
    <div>
      <h1>WebSocket Test Page</h1>
      <p>This page is designed to test WebSocket functionality.</p>
    </div>
  );
}
