defmodule RealtimeWeb.UserSocket do
  use Phoenix.Socket

  channel "project:*", RealtimeWeb.ProjectChannel

  def connect(_params, socket, _connect_info), do: {:ok, socket}
  def id(_socket), do: nil
end
