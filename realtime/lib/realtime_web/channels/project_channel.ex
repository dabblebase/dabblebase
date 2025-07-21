defmodule RealtimeWeb.ProjectChannel do
  use Phoenix.Channel

  def join("project:" <> _id, _params, socket) do
    {:ok, socket}
  end
end
