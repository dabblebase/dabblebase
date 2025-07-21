defmodule Realtime.ProjectsLoader do
  def load_existing_projects do
    {:ok, conn} =
      Postgrex.start_link(
        hostname: "db-admin-cluster",
        port: "5432",
        username: "postgres",
        password: "postgres",
        database: "tinkerbase_admin"
      )

    {:ok, result} =
      Postgrex.query(
        conn,
        "SELECT id, assignment_id, db_name, admin_role_name, encrypted_admin_role_password FROM projects",
        []
      )

    for [project_id, assignment_id, db_name, admin_role_name, encrypted_admin_role_password] <-
          result.rows do
      {:ok, admin_role_password} =
        Realtime.Crypto.decrypt_role_password(
          encrypted_admin_role_password,
          assignment_id
        )

      start_listener(project_id, db_name, admin_role_name, admin_role_password)
    end
  end

  def start_listener(project_id, db_name, admin_role_name, admin_role_password) do
    case Registry.lookup(Realtime.Registry, project_id) do
      [] ->
        spec =
          {Realtime.Listeners.PgListener,
           %{
             project_id: project_id,
             db_name: db_name,
             db_role: admin_role_name,
             db_password: admin_role_password
           }}

        DynamicSupervisor.start_child(Realtime.ListenerSupervisor, spec)

      _ ->
        :ok
    end
  end
end
