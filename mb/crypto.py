from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
import base64
import base58
import json



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

