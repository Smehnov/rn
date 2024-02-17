import os


API_URL = os.environ.get('MERKLEBOT_API_URL', "https://app.merklebot.com/api/api")

API_TOKEN = os.environ.get('MERKLEBOT_USER_TOKEN')
if not API_TOKEN:
    print('MERKLEBOT_USER_TOKEN not set')
    exit(1)
ORGANIZATION_ID = os.environ.get('MERKLEBOT_ORGANIZATION_ID')
if not ORGANIZATION_ID:
    print('MERKLEBOT_ORGANIZATION_ID not set')
    exit(1)
