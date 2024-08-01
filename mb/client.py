import socketio
import readchar
import sys
import signal
import time
from enum import Enum

from mb.settings import ROBOT_SERVER_URL, API_TOKEN, AGENT_SOCKET_PATH 


sio = socketio.Client()

class ConnectionType(Enum):
    PLATFORM = 'platform'
    AGENT = 'agent'

class TerminalSessionRequest:
    def __init__():
       pass 

class Client:
    def __init__(connection_type: ConnectionType):
        self.connection_type = connection_type

    def start_terminal_session(self, job_id):
        self.connect_to_job()
        if self.connection_type==ConnectionType.PLATFORM:
            start_terminal_session()

    def transfer_tar():
        pass


sio.channel_mode = None



def handler(signum, frame):
    pass


@sio.event
def connect(auth = {}):
    print('connection established')


@sio.on("message_to_client")
def message_to_client(data):
    if sio.channel_mode == 'Terminal':
        content = data['content'].get('stdout')
        if content not in ['\x1b[6n', None]:
            sys.stdout.write(content)
            sys.stdout.flush()
    elif sio.channel_mode == 'ArchiveTo':
        print(data)


def message_to_robot(command):
    sio.emit('message_to_robot', {'content': {'type': 'Terminal', 'stdin': command}})

@sio.event
def disconnect():
    print('disconnected from server')

def start_terminal_session(api_key:str, job_id: str):
    sio.channel_mode = "Terminal"
    connect_to_job(api_key, job_id)

    print("===TERMINAL SESSION STARTED===")
    signal.signal(signal.SIGINT, handler)
    time.sleep(1)
    message_to_robot('\n\r')
    while True:
        key = readchar.readchar()
        #print(bytes(key))
        # check Crtl+D
        if key in ['\x04']:
            print('===EXIT TERMINAL SESSION===')
            exit(0)
        
        message_to_robot(key)

def transfer_tar(api_key: str, job_id: str, dest_path: str, encoded_tar: bytes):
    sio.channel_mode = 'ArchiveTo'
    connect_to_job(api_key, job_id)
    time.sleep(1)
    sio.emit('message_to_robot', {'content': {'type': 'Archive', 'dest_path': dest_path, 'data': encoded_tar}})
    sio.wait()
    

def connect_to_job(api_key: str, job_id: str):
    auth = {
        "api_key": api_key,
        "session_type": "CLIENT",
        "job_id": job_id
    }
    sio.connect(ROBOT_SERVER_URL, auth=auth)
    #sio.wait()

if __name__=="__main__":
    pass
