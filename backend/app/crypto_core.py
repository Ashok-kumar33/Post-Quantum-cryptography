import os
import hashlib
from pqcrypto.kem import ml_kem_1024
from pqcrypto.sign import ml_dsa_44, ml_dsa_65
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def generate_keys():
    """Generate an ML-KEM-1024 keypair (exchange) and ML-DSA-65 keypair (signing)."""
    kem_pk, kem_sk = ml_kem_1024.generate_keypair()
    dsa_pk, dsa_sk = ml_dsa_65.generate_keypair()
    return kem_pk, kem_sk, dsa_pk, dsa_sk


def protect_bytes(data: bytes, kem_pk: bytes, dsa_sk: bytes) -> bytes:
    """Wrap a fresh AES-256-GCM key with ML-KEM-1024, encrypt data, sign the package."""
    ct, secret = ml_kem_1024.encrypt(kem_pk)
    key = hashlib.sha256(secret).digest()

    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    enc = cipher.encryptor()
    ct_data = enc.update(data) + enc.finalize()
    tag = enc.tag

    pkg = ct + iv + ct_data + tag
    sig = ml_dsa_44.sign(dsa_sk, pkg)

    return len(sig).to_bytes(4, "big") + sig + len(ct).to_bytes(4, "big") + pkg


def recover_bytes(blob: bytes, kem_sk: bytes, dsa_pk: bytes) -> bytes:
    """Verify signature, then decapsulate the ML-KEM ciphertext and decrypt."""
    sig_len = int.from_bytes(blob[0:4], "big")
    sig = blob[4:4 + sig_len]
    ct_len = int.from_bytes(blob[4 + sig_len:8 + sig_len], "big")
    pkg = blob[8 + sig_len:]

    ml_dsa_44.verify(dsa_pk, pkg, sig)  # raises if tampered

    ct = pkg[:ct_len]
    iv = pkg[ct_len:ct_len + 12]
    ct_data = pkg[ct_len + 12:-16]
    tag = pkg[-16:]

    secret = ml_kem_1024.decrypt(kem_sk, ct)
    key = hashlib.sha256(secret).digest()

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    dec = cipher.decryptor()
    return dec.update(ct_data) + dec.finalize()
