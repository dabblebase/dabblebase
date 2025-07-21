defmodule Realtime.Database do
  @moduledoc """
  The database module provides configurations for connecting to the admin database and the content
  database cluster.
  """
  def admin_db_connection do
    Postgrex.start_link(
      hostname: Application.get_env(:realtime, :admin_db_host),
      port: Application.get_env(:realtime, :admin_db_port),
      username: Application.get_env(:realtime, :admin_db_user),
      password: Application.get_env(:realtime, :admin_db_password),
      database: Application.get_env(:realtime, :admin_db_database)
    )
  end

  @doc """
  Constructs a database URL for the content database using the provided database name, role name, and role password.
  """
  @spec content_db_url(String.t(), String.t(), String.t()) :: String.t()
  def content_db_url(db_name, role_name, role_password) do
    host = Application.get_env(:realtime, :content_db_host)
    port = Application.get_env(:realtime, :content_db_port)
    "postgres://#{role_name}:#{role_password}@#{host}:#{port}/#{db_name}"
  end
end
