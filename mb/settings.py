import os


API_URL = os.environ.get('MERKLEBOT_API_URL', "https://app.merklebot.com/api/api")
ROBOT_SERVER_URL = os.environ.get('MERKLEBOT_ROBOT_SERVER_URL', "https://robots.merklebot.com")
AGENT_SOCKET_PATH = os.environ.get('AGENT_SOCKET_PATH', None)
API_TOKEN = os.environ.get('MERKLEBOT_USER_TOKEN')
if not API_TOKEN and not AGENT_SOCKET_PATH:
    print('MERKLEBOT_USER_TOKEN not set')
    exit(1)
ORGANIZATION_ID = os.environ.get('MERKLEBOT_ORGANIZATION_ID')
if not ORGANIZATION_ID and not AGENT_SOCKET_PATH:
    print('MERKLEBOT_ORGANIZATION_ID not set')
    exit(1)
