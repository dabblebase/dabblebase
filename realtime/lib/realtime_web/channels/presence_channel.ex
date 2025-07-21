defmodule RealtimeWeb.PresenceChannel do
  use Phoenix.Channel
  alias RealtimeWeb.Presence

  # Topic format: "presence:<project_id>"
  def join("presence:" <> project_id, _params, socket) do
    case RealtimeWeb.JoinGuard.authorize_project_join(project_id, socket) do
      {:ok, socket} ->
        send(self(), :after_join)
        {:ok, socket}

      {:error, reason} ->
        {:error, reason}
    end
  end

  def handle_info(:after_join, socket) do
    # Ensure user_id is present
    user_id = socket.assigns[:user_id] || "anonymous"

    {:ok, _} =
      Presence.track(
        socket,
        user_id,
        %{
          online_at: DateTime.utc_now() |> DateTime.to_iso8601()
        }
      )

    push(socket, "presence_state", Presence.list(socket))
    {:noreply, socket}
  end
end
