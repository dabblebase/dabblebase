defmodule Realtime.Crypto do
  @moduledoc """
  Provides the cryptographic functions for working with encrypted database passwords from
  the admin table.
  """

  @doc """
  Decrypts a role password given the encrypted token and the assignment ID.

  Under the hood, this implementation reconstructs the encryption key using an idential
  HKDF implementation to the one used in the Python server, then the Fernet library is used to
  verify the token and return the plaintext password.
  """
  @spec decrypt_role_password(String.t(), integer()) :: {:ok, String.t()} | {:error, any()}
  def decrypt_role_password(token, assignment_id) do
    secret = System.get_env("AUTH_MASTER_SECRET", "REPLACE_ME")

    with {:ok, key} <- derive_key(secret, assignment_id),
         {:ok, plaintext} <- Fernet.verify(token, key: key, enforce_ttl: false) do
      {:ok, plaintext}
    else
      err -> {:error, err}
    end
  end

  @spec derive_key(String.t(), integer()) :: {:ok, String.t()} | {:error, any()}
  defp derive_key(secret, assignment_id) do
    info = Integer.to_string(assignment_id)

    pseudorandom_key = HKDF.extract(:sha256, secret, <<>>)
    derived_key = HKDF.expand(:sha256, pseudorandom_key, 32, info)

    url_safe_key = Base.url_encode64(derived_key)

    {:ok, url_safe_key}
  end
end
