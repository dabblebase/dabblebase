defmodule RealtimeWeb.JoinGuard do
  @moduledoc """
  Shared helpers for channel join authorization.
  """

  @spec authorize_project_join(String.t(), Phoenix.Socket.t(), keyword()) ::
          {:ok, Phoenix.Socket.t()} | {:error, map()}
  def authorize_project_join(
        topic_project_id,
        %Phoenix.Socket{assigns: %{project_id: assigned_project_id}} = socket,
        opts \\ []
      ) do
    if topic_project_id == assigned_project_id do
      {:ok, assign_multiple(socket, opts)}
    else
      {:error, %{reason: "unauthorized"}}
    end
  end

  defp assign_multiple(socket, []), do: socket

  defp assign_multiple(socket, [{key, value} | rest]) do
    socket
    |> Phoenix.Socket.assign(key, value)
    |> assign_multiple(rest)
  end
end
