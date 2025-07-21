defmodule Realtime.Listeners.PgListener do
  use GenServer

  def start_link(%{project_id: id} = opts) do
    GenServer.start_link(__MODULE__, opts, name: via(id))
  end

  defp via(id), do: {:via, Registry, {Realtime.Registry, id}}

  def init(%{project_id: project_id, db_name: db_name, db_role: db_role, db_password: db_password}) do
    {:ok, conn} =
      Postgrex.Notifications.start_link(
        hostname: "db-content-cluster",
        port: "5432",
        username: db_role,
        password: db_password,
        database: db_name
      )

    IO.puts("Listening to changes in database #{db_name} for project #{project_id}")
    Postgrex.Notifications.listen(conn, "table_updates")
    {:ok, %{conn: conn, project_id: project_id}}
  end

  def handle_info({:notification, _conn, _pid, "table_updates", payload}, state) do
    RealtimeWeb.Endpoint.broadcast!("project:#{state.project_id}", "pg_change", %{
      payload: payload
    })

    {:noreply, state}
  end
end
