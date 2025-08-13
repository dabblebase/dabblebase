defmodule RealtimeWeb.BroadcastChannel do
  use Phoenix.Channel

  # Topic format: "broadcast:<project_id>:<channel>"
  def join("broadcast:" <> rest, _params, socket) do
    [project_id, channel_name] = String.split(rest, ":", parts: 2)

    # Verify that the project ID from the token matches the one in the topic
    RealtimeWeb.JoinGuard.authorize_project_join(project_id, socket, channel_name: channel_name)
  end

  def handle_in("message", %{"payload" => payload}, socket) do
    broadcast!(socket, "message", payload)
    {:noreply, socket}
  end
end
