defmodule Realtime.Database do
  @moduledoc """
  The database module provides configurations for connecting to the admin database and the content
  database cluster.
  """

  def admin_db_config do
    %{
      hostname: System.get_env("ADMIN_DB_HOST"),
      port: String.to_integer(System.get_env("ADMIN_DB_PORT", "5432")),
      username: System.get_env("ADMIN_DB_USER"),
      password: System.get_env("ADMIN_DB_PASSWORD"),
      database: System.get_env("ADMIN_DB_NAME")
    }
  end

  @doc """
  Constructs a database URL for the content database using the provided database name, role name, and role password.
  """
  @spec content_db_url(String.t(), String.t(), String.t()) :: String.t()
  def content_db_url(db_name, role_name, role_password) do
    "postgres://#{role_name}:#{role_password}@db-content-cluster:5432/#{db_name}"

    # "postgres://#{role_name}:#{role_password}@#{System.get_env("CONTENT_DB_HOST")}:#{System.get_env("CONTENT_DB_PORT")}/#{db_name}"
  end
end
