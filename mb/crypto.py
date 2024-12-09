from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric import x25519, ed25519
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.exceptions import InvalidKey, InvalidSignature

import hashlib



import base64
import base58
import json
from dataclasses import dataclass



def generate_key():
    private_key = Ed25519PrivateKey.generate()

    return private_key
def read_private_key(path):
    with open(path, 'r') as f:
        data = base64.b64decode(f.read())
    
    sk_data, pk_data = data[:32], data[32:]
    private_key = Ed25519PrivateKey.from_private_bytes(sk_data)
    return private_key

def get_key_bytes(private_key):
    public_key = private_key.public_key()
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return private_key_bytes, public_key_bytes

def get_base_64(private_key, mode='both'):
    private_key_bytes, public_key_bytes = get_key_bytes(private_key)
    if mode=='sk':
       private_key_base64 = base64.b64encode(private_key_bytes).decode('ascii')
       return private_key_base64
    elif mode=='pk': 
        public_key_base64 = base64.b64encode(public_key_bytes).decode('ascii')
        return public_key_base64
    elif mode=='both':
        public_key_base64 = base64.b64encode(public_key_bytes).decode('ascii')
        private_key_base64 = base64.b64encode(private_key_bytes+public_key_bytes).decode('ascii')
        return private_key_base64, public_key_base64
    
def base64_to_bytes(encoded):
    return base64.b64decode(encoded)
    
def get_peer_id(public_key_bytes):
    peer_id= base58.b58encode(b'\x00$\x08\x01\x12 ' + public_key_bytes).decode('ascii')
    return peer_id


enc_msg = {'message': 'sCwgFi9xOA2vrAquQTshowIW2bz0slw9UqU7ON8mhtu+ajbZkoq1ifqFObItTyuOrDhYwp8lOjLgMKAJcCQpTLB+u7S4bWqTr952Fu4Fy/F1HDimdiw/S+/LNLatpyylm3dpXr7Uf1sdTgsgeivkjD7TD5Qc0AMwEdqL5Jb/V09XuBIjiCJdesF7sYa4pDPX9OXNAtAhQTTsXzr4NzH/GTwpzlhK2zqs/QMzrdq/3ZlOONxR1AKS87d4XG0baWKayc84MecP2Nim9RcDJZ/rl4iGBislf8bIFEBmOtr8FknqUOjKI5+bf/fHVnKTeS7bOGiDsMJWlw==',
           'encryption': {
               'ephemeral_public': [180, 5, 251, 81, 129, 249, 224, 50, 64, 105, 137, 134, 240, 18, 238, 9, 171, 208, 2, 207, 36, 11, 89, 129, 104, 162, 216, 77, 135, 205, 206, 14],
               'nonce': [178, 18, 180, 9, 203, 118, 210, 199, 209, 146, 171, 11]
            },
           'sign': [24, 72, 18, 14, 106, 12, 216, 208, 160, 232, 63, 64, 146, 182, 201, 120, 121, 169, 232, 88, 200, 2, 65, 54, 247, 64, 16, 212, 153, 45, 196, 40, 170, 128, 35, 82, 147, 254, 188, 77, 208, 162, 158, 9, 204, 226, 35, 39, 37, 136, 232, 169, 77, 80, 216, 158, 17, 213, 199, 223, 149, 246, 82, 10],
           'to': '12D3KooWC2TBgekAAvRPe3GMX5rjQeJf3eNKZ3ADfYwfxHYNPLkU',
           'public_key': [217, 43, 111, 52, 190, 17, 50, 251, 175, 173, 247, 222, 15, 224, 199, 143, 19, 126, 204, 193, 91, 211, 23, 237, 52, 128, 121, 108, 15, 147, 208, 56]}

@dataclass
class EncryptedMessage:
    """Represents an encrypted message with all necessary components for decryption"""
    enc_msg: bytes
    ephemeral_public: bytes
    nonce: bytes
    sign: bytes
    from_pk: bytes

    
    @classmethod
    def from_dict(cls, data: dict)->'EncryptedMessage':
        return cls(
            enc_msg=base64.b64decode(data['message']),
            ephemeral_public=bytes(data['encryption']['ephemeral_public']),
            nonce=bytes(data['encryption']['nonce']),
            sign=bytes(data['sign']),
            from_pk=bytes(data['public_key'])
        )



def _derive_x25519_private(ed25519_key: Ed25519PrivateKey) -> x25519.X25519PrivateKey:
    private_bytes = ed25519_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    # Hash the private key to get material for X25519 key
    digest = hashes.Hash(hashes.SHA256())
    digest.update(private_bytes)
    seed = digest.finalize()
    return x25519.X25519PrivateKey.from_private_bytes(seed[:32])

def _derive_x25519_public(ed25519_public: Ed25519PublicKey) -> x25519.X25519PublicKey:
    public_bytes = ed25519_public.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    digest = hashes.Hash(hashes.SHA256())
    digest.update(public_bytes)
    seed = digest.finalize()
    return x25519.X25519PublicKey.from_public_bytes(seed[:32])

def decrypt_message(encrypted_message_data, secret_key):
    encrypted_message = EncryptedMessage.from_dict(encrypted_message_data)
    private_key = Ed25519PrivateKey.from_private_bytes(secret_key)
    public_x25519 = _derive_x25519_public(private_key.public_key())
    
    print(encrypted_message)

    sender_public = Ed25519PublicKey.from_public_bytes(
        encrypted_message.from_pk
    )
    
    
    try:
        res = sender_public.verify(encrypted_message.sign, encrypted_message.enc_msg)
        print('res', res)
    except InvalidSignature:
        raise InvalidSignature("Invalid message signature")

    # Convert ephemeral public bytes to key
    ephemeral_public = x25519.X25519PublicKey.from_public_bytes(
        encrypted_message.ephemeral_public
    )

    # Perform X25519 DH
    x25519_private = _derive_x25519_private(private_key)
    print('public x25519 ', [x for x in public_x25519.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )])

    print('ephemeral_public', [x for x in ephemeral_public.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )])

    dh1 = x25519_private.exchange(ephemeral_public)
    print("dh1", [x for x in dh1])
    dh2 = x25519_private.exchange(public_x25519)
    print("dh2", [x for x in dh2])

    # Derive encryption key
    hash_obj = hashlib.sha256()
    hash_obj.update(dh1)
    hash_obj.update(dh2)
    key = hash_obj.digest()
    print('key', [x for x in key])

    # Decrypt the message
    cipher = ChaCha20Poly1305(key)
    try:
        plaintext = cipher.decrypt(encrypted_message.nonce, encrypted_message.enc_msg, None)
        return plaintext
    except Exception as e:
        raise InvalidKey("Decryption failed") from e

    

