"""Helper functions for authentication-related cryptography."""

import jwt
import base64
import secrets
from typing import Any, Union
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.fernet import Fernet


def generate_serialied_rsa_keypair() -> tuple[str, str]:
    """Generates a serialized RSA keypair (private_key, public_key)"""
    private_key, public_key = _generate_rsa_keypair()
    return _serialize_rsa_keypair(private_key, public_key)


def _generate_rsa_keypair() -> tuple[RSAPrivateKey, RSAPublicKey]:
    """Generate an RSA keypair."""
    # Generate the private and public key
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    return private_key, public_key


def _serialize_rsa_keypair(
    private_key: RSAPrivateKey, public_key: RSAPublicKey
) -> tuple[str, str]:
    """Generates the DER-encoded base-64 strings for any given RSA keypair."""
    # Create the DER-encoded strings for the private and public keys
    der_private = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    der_public = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    # DER0-encoded strings are binary, so we need to encode them to base64 to make them string-friendly
    der_private_b64 = base64.b64encode(der_private)
    der_public_b64 = base64.b64encode(der_public)
    # Return the DER-encoded strings as UTF-8
    der_private_str = der_private_b64.decode("utf-8")
    der_public_str = der_public_b64.decode("utf-8")

    return der_private_str, der_public_str


def deserialize_rsa_keypair(
    private_key_str: str, public_key_str: str
) -> tuple[RSAPrivateKey, RSAPublicKey]:
    """Deserializes the DER-encoded base-64 strings into an RSA keypair."""
    # Decode the base64 strings to get the DER-encoded bytes
    der_private = base64.b64decode(private_key_str.encode("utf-8"))
    der_public = base64.b64decode(public_key_str.encode("utf-8"))
    # Deserialize the private and public keys from the DER-encoded bytes
    private_key = serialization.load_der_private_key(der_private, password=None)
    public_key = serialization.load_der_public_key(der_public)
    return private_key, public_key  # type: ignore


def hkdf_derive_encryption_key(secret: str, data: Union[str, int]) -> bytes:
    """Derives an encryption key using HKDF from a secret and additional data."""
    data_str = str(data)
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,  # 32 bytes = 256 bits (SHA-256)
        salt=None,
        info=data_str.encode("utf-8"),
    )
    derived_key = hkdf.derive(secret.encode("utf-8"))
    # Convert the derived key to a URL-safe base64-encoded string so that it can be
    # used as a key for Fernet encryption
    url_safe_key = base64.urlsafe_b64encode(derived_key)
    return url_safe_key


def encrypt(value: str, key: bytes) -> str:
    """Encrypts a value using the provided key."""
    f = Fernet(key)
    encrypted_value = f.encrypt(value.encode("utf-8"))
    return encrypted_value.decode("utf-8")


def decrypt(encrypted_value: str, key: bytes) -> str:
    """Decrypts an encrypted value using the provided key."""
    f = Fernet(key)
    decrypted_value = f.decrypt(encrypted_value.encode("utf-8"))
    return decrypted_value.decode("utf-8")


def sign_jwt_with_asymmetric_keys(data: dict[str, Any], private_key: str) -> str:
    """Signs a JWT token for use with asymmetric keys (RS256 algorithm)."""
    # The `jwt.encode` function expects the private key to be in PEM format, so we need to
    # convert the DER-encoded private key to PEM format first.
    pem_private_key = _convert_private_key_str_to_pem_key(private_key)
    # Encode the data into a JWT token using the private key
    token = jwt.encode(data, pem_private_key, algorithm="RS256")
    return token


def decode_jwt_with_asymmetric_keys(token: str, public_key: str) -> dict[str, Any]:
    """Decodes a JWT token using the public key."""
    # The `jwt.decode` function expects the public key to be in PEM format, so we need to
    # convert the DER-encoded public key to PEM format first.
    pem_public_key = _convert_public_key_str_to_pem_key(public_key)
    decoded = jwt.decode(token, pem_public_key, algorithms=["RS256"])
    return decoded


def sign_jwt_with_symmetric_key(data: dict[str, Any], secret: str) -> str:
    """Signs a JWT token for use with symmetric keys (HS256 algorithm)."""
    # Encode the data into a JWT token using the secret key
    token = jwt.encode(data, secret, algorithm="HS256")
    return token


def decode_jwt_with_symmetric_key(token: str, secret: str) -> dict[str, Any]:
    """Decodes a JWT token using the symmetric secret key."""
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    return decoded


def _convert_private_key_str_to_pem_key(private_key: str) -> bytes:
    """Converts a private key string into the PEM format, required to sign the JWT"""
    der_private_bytes = base64.b64decode(private_key.encode("utf-8"))
    der_private_key = serialization.load_der_private_key(
        der_private_bytes, password=None
    )
    pem_private_key = der_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    if not pem_private_key:
        raise ValueError("Failed to convert DER private key to PEM format.")
    return pem_private_key


def _convert_public_key_str_to_pem_key(public_key: str) -> bytes:
    """Converts a public key string into the PEM format, required to verify the JWT"""
    der_public_bytes = base64.b64decode(public_key.encode("utf-8"))
    der_public_key = serialization.load_der_public_key(der_public_bytes)
    pem_public_key = der_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    if not pem_public_key:
        raise ValueError("Failed to convert DER public key to PEM format.")
    return pem_public_key


def generate_secure_password() -> str:
    """Generates a secure password"""
    raw = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")
