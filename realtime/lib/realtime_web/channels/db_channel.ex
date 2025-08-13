defmodule RealtimeWeb.DbChannel do
  use Phoenix.Channel

  # Topic format: "db:<project_id>"
  def join("db:" <> project_id, _params, socket) do
    RealtimeWeb.JoinGuard.authorize_project_join(project_id, socket)
  end
end
