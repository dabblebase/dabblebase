defmodule Realtime.AdminListener do
  use GenServer

  def start_link(_), do: GenServer.start_link(__MODULE__, nil, name: __MODULE__)

  def init(_) do
    {:ok, conn} =
      Postgrex.Notifications.start_link(
        hostname: "db-admin-cluster",
        port: "5432",
        username: "postgres",
        password: "postgres",
        database: "tinkerbase_admin"
      )

    Postgrex.Notifications.listen(conn, "new_project")
    Realtime.ProjectsLoader.load_existing_projects()
    {:ok, conn}
  end

  def handle_info({:notification, _conn, _pid, "new_project", payload}, conn) do
    IO.puts("Received new project notification: #{payload}")

    %{
      "project_id" => project_id,
      "assignment_id" => assignment_id,
      "db_name" => db_name,
      "admin_db_role" => admin_db_role,
      "encrypted_admin_db_password" => encrypted_admin_db_password
    } = Jason.decode!(payload)

    admin_db_password =
      Realtime.Crypto.decrypt_role_password(encrypted_admin_db_password, assignment_id)

    Realtime.ProjectsLoader.start_listener(project_id, db_name, admin_db_role, admin_db_password)
    {:noreply, conn}
  end
end
