import os

USER_KEY_PATH="owner.key"
AGENT_SOCKET_PATH = os.environ.get('AGENT_SOCKET_PATH', None)
TERMINAL_KEYPRESS_DELAY = float(os.environ.get('TERMINAL_KEYPRESS_DELAY', 0.1))