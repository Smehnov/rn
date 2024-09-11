from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
import base64
import typer
import json
from mb.crypto import generate_key, get_key_bytes, get_base_64, base64_to_bytes, get_peer_id



agent_app = typer.Typer()


@agent_app.command()
def gen(key_path):
    private_key = generate_key()
    private_key_base64, public_key_base64 = get_base_64(private_key)
    print("Public Key:", public_key_base64)
    peer_id = get_peer_id(base64_to_bytes(public_key_base64))
    print("PeerId:", peer_id)
    with open(key_path, 'w') as f:
        f.write(private_key_base64)


@agent_app.command()
def public(key_path):
    with open(key_path, 'r') as f:
        encoded = f.read()
    
    data = base64.b64decode(encoded)
    sk_data = data[:32]
    private_key = Ed25519PrivateKey.from_private_bytes(sk_data)
    print('Public key:', get_base_64(private_key ,mode='pk'))

@agent_app.command()
def update_config(key_path, config_path):
    data = None
    with open(key_path, 'r') as f:
        data = base64.b64decode(f.read())
    
    sk_data, pk_data = data[:32], data[32:]
    private_key = Ed25519PrivateKey.from_private_bytes(sk_data)
    public_key = Ed25519PublicKey.from_public_bytes(pk_data)
    with open(config_path, 'r') as f:
        config = json.load(f)
        print(config)

    


    

    

    