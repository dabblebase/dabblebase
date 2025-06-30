"""Testing suite for the health service."""

from ...services import auth_crypto as crypto


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
    secret = "AUTH_MASTER_SECRET"
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
