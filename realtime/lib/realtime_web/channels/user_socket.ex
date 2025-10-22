defmodule RealtimeWeb.UserSocket do
  use Phoenix.Socket

  channel "db:*", RealtimeWeb.DbChannel
  channel "broadcast:*", RealtimeWeb.BroadcastChannel
  channel "presence:*", RealtimeWeb.PresenceChannel

  @spec connect(map(), any(), any()) :: :error | {:ok, Phoenix.Socket.t()}
  def connect(
        %{"project_token" => project_token, "auth_token" => auth_token},
        socket,
        _connect_info
      ) do
    case Realtime.Auth.verify_project_token(project_token) do
      {:ok, %{"project_id" => project_id}} ->
        case Realtime.Auth.verify_auth_token(project_id, auth_token) do
          {:ok, %{"id" => user_id}} ->
            socket =
              socket
              |> assign(:project_id, Integer.to_string(project_id))
              |> assign(:user_id, Integer.to_string(user_id))

            {:ok, socket}

          {:error, _} ->
            :error
        end

      {:error, _} ->
        :error
    end
  end

  @spec connect(map(), any(), any()) :: :error | {:ok, Phoenix.Socket.t()}
  def connect(
        %{"project_token" => project_token},
        socket,
        _connect_info
      ) do
    case Realtime.Auth.verify_project_token(project_token) do
      {:ok, %{"project_id" => project_id}} ->
        {:ok, assign(socket, :project_id, Integer.to_string(project_id))}

      {:error, _} ->
        :error
    end
  end

  def id(_socket), do: nil
end
