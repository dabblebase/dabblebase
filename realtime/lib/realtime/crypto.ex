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
  def derive_key(secret, assignment_id) do
    info = Integer.to_string(assignment_id)

    pseudorandom_key = HKDF.extract(:sha256, secret, <<>>)
    derived_key = HKDF.expand(:sha256, pseudorandom_key, 32, info)

    url_safe_key = Base.url_encode64(derived_key)

    {:ok, url_safe_key}
  end

  @doc """
  Converts a base64-encoded DER public key string into a PEM-formatted string.
  """
  @spec convert_base64_der_to_pem(String.t()) :: {:ok, String.t()} | {:error, any()}
  def convert_base64_der_to_pem(base64_der) do
    with {:ok, der} <- Base.decode64(base64_der),
         {:ok, pem_entry} <- wrap_der_in_pem(der) do
      {:ok, pem_entry}
    else
      :error -> {:error, "Invalid base64 DER input"}
      error -> {:error, error}
    end
  end

  defp wrap_der_in_pem(der) do
    # :public_key.der_encode doesn't help here, since we already have DER
    pem_lines =
      der
      |> Base.encode64()
      # Insert newlines every 64 chars
      |> String.replace(~r/.{64}/, "\\0\n")
      |> String.trim()
      |> then(&["-----BEGIN PUBLIC KEY-----\n", &1, "\n-----END PUBLIC KEY-----"])
      |> IO.iodata_to_binary()

    {:ok, pem_lines}
  end
end
