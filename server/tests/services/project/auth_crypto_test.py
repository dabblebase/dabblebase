"""Testing suite for the health service."""

import jwt
from ....services.project import auth_crypto as crypto
from ....env import env


def test_generate_rsa_keypair():
    private_key, public_key = crypto._generate_rsa_keypair()
    private_key_str, public_key_str = crypto._serialize_rsa_keypair(
        private_key, public_key
    )

    assert isinstance(private_key_str, str), "Private key should be a string"
    assert isinstance(public_key_str, str), "Public key should be a string"

    deserialized_private_key, deserialized_public_key = crypto.deserialize_rsa_keypair(
        private_key_str, public_key_str
    )

    assert isinstance(
        deserialized_private_key, crypto.RSAPrivateKey
    ), "Deserialized private key should be an RSAPrivateKey"
    assert isinstance(
        deserialized_public_key, crypto.RSAPublicKey
    ), "Deserialized public key should be an RSAPublicKey"

    reserialized_private_key_str, reserialized_public_key_str = (
        crypto._serialize_rsa_keypair(deserialized_private_key, deserialized_public_key)
    )

    assert (
        private_key_str == reserialized_private_key_str
    ), "Deserialized private key should match original"
    assert (
        public_key_str == reserialized_public_key_str
    ), "Deserialized public key should match original"


def test_encrpytion_decryption_with_hkdf_keygen():
    secret = env.AUTH_MASTER_SECRET
    project_id = "1"
    private_key, _ = crypto.generate_serialied_rsa_keypair()
    encryption_key = crypto.hkdf_derive_encryption_key(secret, project_id)
    assert isinstance(
        encryption_key, bytes
    ), "Encryption key produced by hkdf should be bytes"

    encrypted_private_key = crypto.encrypt(private_key, encryption_key)
    assert isinstance(encrypted_private_key, str), "Encrypted private key should be str"

    decrypted_private_key = crypto.decrypt(encrypted_private_key, encryption_key)
    assert (
        decrypted_private_key == private_key
    ), "Decrypted private key should match original"


def test_jwt_signing_and_verifying_with_asymmetric_keys():
    """Tests that a project's public key can verify a JWT signed by its private key."""
    private_key, public_key = crypto.generate_serialied_rsa_keypair()
    payload = {"id": 1}

    # Sign the JWT with the private key
    token = crypto.sign_jwt_with_asymmetric_keys(payload, private_key)

    # Decode the JWT using the public key
    decoded_payload = crypto.decode_jwt_with_asymmetric_keys(token, public_key)

    assert (
        decoded_payload["id"] == payload["id"]
    ), "Decoded JWT should match original payload"
