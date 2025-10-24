defmodule Realtime.Auth do
  @moduledoc """
  Verifies JWTs signed by the FastAPI backend, using a project-specific public key.
  """

  alias Joken.Signer

  @doc """
  Verifies a JWT and returns {:ok, claims} or {:error, reason}.
  """
  def verify_project_token(project_token) do
    # For development/testing purposes, let's use a simpler approach
    # This matches the HMAC signing key logic from the Python server
    with {:ok, %{"project_id" => project_id}} <- Joken.peek_claims(project_token),
         {:ok, signing_key} <- derive_project_signing_key(project_id),
         signer <- Signer.create("HS256", signing_key),
         {:ok, claims} <- Joken.verify(project_token, signer) do
      {:ok, claims}
    else
      error ->
        IO.inspect(error, label: "[auth] Project token verification failed")
        {:error, error}
    end
  end

  def verify_auth_token(project_id, auth_token) do
    with {:ok, _project_verification_key, auth_public_key} <-
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
        "SELECT project_verification_key, auth_public_key FROM projects WHERE id = $1",
        [
          project_id
        ]
      )

    GenServer.stop(conn)

    case result do
      {:ok, %Postgrex.Result{rows: [[project_verification_key, auth_public_key]]}} ->
        {:ok, project_verification_key, auth_public_key}

      _ ->
        {:error, :project_not_found}
    end
  end

  defp derive_project_signing_key(project_id) do
    # Use the existing crypto module's derive_key function
    # This replicates the Python server's HKDF key derivation logic
    master_secret = System.get_env("AUTH_MASTER_SECRET", "REPLACE_ME")

    case Realtime.Crypto.derive_key(master_secret, project_id) do
      {:ok, encryption_key} ->
        # Now we need to fetch and decrypt the project's signing key
        # For development/testing, let's use the encryption key as the signing key
        # In production, this would decrypt the stored project_encrypted_signing_key
        {:ok, project_signing_key} =
          fetch_and_decrypt_project_signing_key(project_id, encryption_key)

        {:ok, project_signing_key}

      error ->
        {:error, error}
    end
  end

  defp fetch_and_decrypt_project_signing_key(project_id, encryption_key) do
    {:ok, conn} = Realtime.Database.admin_db_connection()

    result =
      Postgrex.query(
        conn,
        "SELECT project_encrypted_signing_key FROM projects WHERE id = $1",
        [project_id]
      )

    GenServer.stop(conn)

    case result do
      {:ok, %Postgrex.Result{rows: [[encrypted_signing_key]]}} ->
        # Decrypt the signing key using Fernet (same as Python server)
        case Fernet.verify(encrypted_signing_key, key: encryption_key, enforce_ttl: false) do
          {:ok, decrypted_key} ->
            {:ok, decrypted_key}

          error ->
            IO.inspect(error, label: "[auth] Failed to decrypt project signing key")
            {:error, error}
        end

      _ ->
        {:error, :project_not_found}
    end
  end
end
