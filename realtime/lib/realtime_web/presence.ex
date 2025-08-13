defmodule RealtimeWeb.Presence do
  use Phoenix.Presence,
    otp_app: :realtime,
    pubsub_server: Realtime.PubSub
end
