defmodule Realtime.Auth do
  @moduledoc """
  Verifies JWTs signed by the FastAPI backend, using a project-specific public key.
  """

  alias Joken.Signer

  @doc """
  Verifies a JWT and returns {:ok, claims} or {:error, reason}.
  """
  def verify_realtime_token(realtime_token) do
    with {:ok, %{"project_id" => project_id}} <- Joken.peek_claims(realtime_token),
         {:ok, realtime_verification_key, _auth_public_key} <-
           fetch_verification_keys(project_id),
         {:ok, pem_key} <- Realtime.Crypto.convert_base64_der_to_pem(realtime_verification_key),
         signer <- Signer.create("RS256", %{"pem" => pem_key}),
         {:ok, claims} <- Joken.verify(realtime_token, signer) do
      {:ok, claims}
    else
      error ->
        IO.inspect(error, label: "[auth] Realtime token verification failed")
        {:error, error}
    end
  end

  def verify_auth_token(project_id, auth_token) do
    with {:ok, _realtime_verification_key, auth_public_key} <-
           fetch_verification_keys(project_id),
         {:ok, pem_key} <- Realtime.Crypto.convert_base64_der_to_pem(auth_public_key),
         signer <- Signer.create("RS256", %{"pem" => pem_key}),
         {:ok, claims} <- Joken.verify(auth_token, signer) do
      {:ok, claims}
    else
      error ->
        IO.inspect(error, label: "[auth] Auth token verification failed")
        {:error, error}
    end
  end

  defp fetch_verification_keys(project_id) do
    {:ok, conn} = Realtime.Database.admin_db_connection()

    result =
      Postgrex.query(
        conn,
        "SELECT realtime_verification_key, auth_public_key FROM projects WHERE id = $1",
        [
          project_id
        ]
      )

    GenServer.stop(conn)

    case result do
      {:ok, %Postgrex.Result{rows: [[realtime_verification_key, auth_public_key]]}} ->
        {:ok, realtime_verification_key, auth_public_key}

      _ ->
        {:error, :project_not_found}
    end
  end
end
