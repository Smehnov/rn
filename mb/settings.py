import os

USER_KEY_PATH=os.environ.get('USER_KEY_PATH', 'owner.key')
OWNER_KEY=os.environ.get('OWNER_KEY')
AGENT_SOCKET_PATH = os.environ.get('AGENT_SOCKET_PATH', None)
AGENT_RPC = os.environ.get('AGENT_RPC', None)
TERMINAL_KEYPRESS_DELAY = float(os.environ.get('TERMINAL_KEYPRESS_DELAY', 0.1))

