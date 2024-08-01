import socket
import os
import json
import pprint
import time
import sys
import threading
import signal
import readchar
import traceback
import re
from mb.settings import AGENT_SOCKET_PATH

def handler(signum, frame):
    pass


class Agent:
    subscribed_functions = []


    def __init__(self, socket_path ):
        self.socket_path = socket_path

    def send_request(self, action, content={}, to=""):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(os.path.realpath(self.socket_path))
        message = {"action": action}
        if content:
            message["content"] = {
                "content": content, 
                "to": to 
            }
        client.sendall(json.dumps(message).encode())
        response = client.recv(65536).decode()
        client.close()
        return json.loads(response)

    def notify_subscribers(self, message):
        for func in self.subscribed_functions:
            try:
                message = '[' + message.replace('}{', '},{') + ']'
 
                objs = json.loads(message)

                for obj in objs:
                    try:
                        func(obj)
                        
                    except:
                        traceback.print_exc()
            except:
                print("ERROR WHILE DECODING MESSAGE: ", message)
                traceback.print_exc()
    def receive_messages(self, socket):
        while True:
            time.sleep(0.05)
            response = socket.recv(2048).decode()
            if response:
                self.notify_subscribers(response)

    def subscribe(self):
        def decorator(func):
            self.subscribed_functions.append(func)
            return func
        return decorator
 

    def start_receiving(self):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(os.path.realpath(self.socket_path))
        client.sendall(json.dumps({"action": "/subscribe_messages"}).encode())

        receive_thread = threading.Thread(target=self.receive_messages, args=(client,))
        receive_thread.daemon = True
        print('ready to start thread')
        receive_thread.start()
        print('thread started')
    def send_job_message(self, robot_peer_id, job_id, content):
       self.send_request("/send_message", {
                "type": "JobMessage",
                "job_id": job_id,
                "content": content
       }, robot_peer_id

       ) 
    def start_tunnel_to_job(self, robot_peer_id, job_id, self_peer_id):
        self.start_receiving()
        self.robot_peer_id = robot_peer_id
        self.job_id = job_id
        self.self_peer_id = self_peer_id
        self.send_request("/send_message", {
                "type": "StartTunnelReq",
                "job_id": job_id,
                "peer_id": self_peer_id
        }, robot_peer_id) 

    def send_terminal_command(self, command):
        self.send_job_message(self.robot_peer_id, self.job_id,
            { 
                "type": "Terminal",
                "stdin": command 
            })
    def start_job(self, robot_peer_id, job_id, job_type, job_args):
        self.send_request('/send_message', {
            "id": job_id,
            "robot_id": robot_peer_id,
            "type": "StartJob",
            "job_type": job_type,#"docker-container-launch",
            "status": "pending",
            "args": json.dumps(job_args)
        }, robot_peer_id)

    def start_terminal_session(self, robot_peer_id:str, job_id: str):

        @self.subscribe()
        def got_message(data):
            if self.channel_mode=='Terminal' and 'message' in data:
                content = data['message'].get('TerminalMessage')
                if content not in ['\x1b[6n', None]:
                    sys.stdout.write(content)
                    sys.stdout.flush()

        self.channel_mode = "Terminal"
        local_devices = self.send_request("/local_robots")
        pprint.pprint(local_devices)
        self.start_tunnel_to_job(robot_peer_id, job_id, local_devices['self_peer_id'])

        print("===TERMINAL SESSION STARTED===")
        signal.signal(signal.SIGINT, handler)
        time.sleep(1)
        self.send_terminal_command('\n\r')
        while True:
            key = readchar.readchar()
            # check Crtl+D
            if key in ['\x04']:
                print('===EXIT TERMINAL SESSION===')
                exit(0)
            
            self.send_terminal_command(key)




def main():
    start_terminal_session('12D3KooWKiQrCdM7uvs39xcksfU13f68zwYpTJB5b4KwVhXsov7Y', '66a7d0f5a5e85e40e4e89508')

if __name__=='__main__':
    main()