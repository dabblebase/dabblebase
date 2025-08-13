# Realtime

To start your Phoenix server:

- Run `mix setup` to install and setup dependencies
- Start Phoenix endpoint with `mix phx.server` or inside IEx with `iex -S mix phx.server`

Now you can visit [`localhost:4000`](http://localhost:4000) from your browser.

Ready to run in production? Please [check our deployment guides](https://hexdocs.pm/phoenix/deployment.html).

## Learn more

- Official website: https://www.phoenixframework.org/
- Guides: https://hexdocs.pm/phoenix/overview.html
- Docs: https://hexdocs.pm/phoenix
- Forum: https://elixirforum.com/c/phoenix-forum
- Source: https://github.com/phoenixframework/phoenix

## NOTE:

Working testing component:

```ts
import { Socket } from "phoenix";
import { useEffect } from "react";

export default function TestPage() {
  useEffect(() => {
    // Create a socket connection
    const socket = new Socket("ws://localhost:8000/ws");

    socket.connect();

    // Join the channel
    const channel = socket.channel("project:1", {});

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
```

For testing presence:

```ts
import { Socket, Channel } from "phoenix";
import { useEffect, useState } from "react";

export default function PresenceTestPage() {
  const [presenceChannel, setPresenceChannel] = useState<Channel | null>(null);
  const [presenceList, setPresenceList] = useState({});

  useEffect(() => {
    const socket = new Socket("ws://localhost:8000/ws", {
      params: {
        realtime_token: "...",
        auth_token: "...",
      },
    });

    socket.connect();

    const chan = socket.channel("presence:1", {});

    chan
      .join()
      .receive("ok", (resp) => {
        console.log("✅ Joined presence channel", resp);
        setPresenceChannel(chan);
      })
      .receive("error", (resp) => {
        console.error("❌ Unable to join presence channel", resp);
      });

    chan.on("presence_state", (state) => {
      console.log("📣 Presence state", state);
      setPresenceList(state);
    });

    return () => {
      chan.leave();
    };
  }, []);

  return (
    <div>
      <h1>Presence Test</h1>
      <pre>{JSON.stringify(presenceList, null, 2)}</pre>
    </div>
  );
}
```
