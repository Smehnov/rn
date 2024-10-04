import socket
from websockets.sync.client import connect as ws_connect
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
from mb.settings import TERMINAL_KEYPRESS_DELAY
from mb.crypto import generate_key, get_key_bytes, get_base_64, get_peer_id, read_private_key, base64_to_bytes
import time

def handler(signum, frame):
    pass

class MessageResponse:
    def __init__(self):
        pass

class Agent:
    subscribed_functions = []


    def __init__(self, USER_KEY_PATH, AGENT_RPC, AGENT_SOCKET_PATH, OWNER_KEY):
        if AGENT_RPC is None and AGENT_SOCKET_PATH is None:
            print("env not set: AGENT_RPC or AGENT_SOCKET_PATH")
            exit()

        self.OWNER_KEY = OWNER_KEY
        self.wait_message = False
        self.socket_path = AGENT_SOCKET_PATH 
        self.rpc_url = AGENT_RPC
        self.private_key = read_private_key(USER_KEY_PATH)
        sk, pk = get_key_bytes(self.private_key)
        self.pk = pk
        self.peer_id = get_peer_id(self.pk)
        self.terminal_messages_queue = []


    def wait(self):
        while self.wait_message:
            time.sleep(0.1)
    def identify_robot_peer_id(self, robot_id: str):
        if robot_id is None:
            return None
        config = self.get_config()
        robots = config.get('robots', [])
        users = config.get('users', [])
        name_to_peer_id = dict([[robot['name'], robot['robot_peer_id']] for robot in robots])
        name_to_peer_id_users = dict([[user['username'], get_peer_id(base64_to_bytes(user['public_key']))] for user in users])
        return name_to_peer_id.get(robot_id, name_to_peer_id_users.get(robot_id, robot_id))

    def send_request(self, action, content={}, to="", signed_message={}, action_param=None):
        if to:
            to = self.identify_robot_peer_id(to)
        message = {"action": action}
        if content:
            message["content"] = {
                "content": content, 
                "to": to 
            }
        if signed_message:
            message["signed_message"] = signed_message
        
        if action_param:
            message["action_param"] = action_param
        response = ""
        if self.rpc_url:
            websocket = ws_connect(self.rpc_url)
            websocket.send(json.dumps(message))
            response = websocket.recv()
        elif self.socket_path:        
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(os.path.realpath(self.socket_path))
    
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
                    if 'message' in obj:
                        obj = json.loads(obj['message'])
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
            response = ""
            if self.rpc_url:
                response = socket.recv()
            elif self.socket_path:
                response = socket.recv(65536).decode()
            if response:
                self.notify_subscribers(response)

    def subscribe(self):
        def decorator(func):
            self.subscribed_functions.append(func)
            return func
        return decorator
 

    def start_receiving(self):
        client = None
        msg = json.dumps({"action": "/subscribe_messages", "action_param": self.peer_id})
        if self.rpc_url:
            client = ws_connect(self.rpc_url)
            client.send(msg)
        elif self.socket_path:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(os.path.realpath(self.socket_path))
            client.sendall(msg).encode()

        receive_thread = threading.Thread(target=self.receive_messages, args=(client,))
        receive_thread.daemon = True
        receive_thread.start()
        print('receiver started')

    def send_terminal_messages(self):
        last_send_time = time.time()
        message_to_send = ""
        while True:
            time.sleep(TERMINAL_KEYPRESS_DELAY)
            while len(self.terminal_messages_queue)>0:
                message_to_send+=self.terminal_messages_queue.pop(0)
            if len(message_to_send)>0:
                self.send_terminal_command(message_to_send)
                message_to_send = ""
            
    def start_terminal_sender(self):
        terminal_thread = threading.Thread(target=self.send_terminal_messages, args=())
        terminal_thread.daemon = True
        terminal_thread.start()
    
    def send_signed_message(self, message:dict):
        message_str = json.dumps(message, separators=(',', ':'))
        sign = self.private_key.sign(message_str.encode('utf-8'))
        self.send_request('/send_signed_message',signed_message={
            "sign": [x for x in sign],
            "public_key": [x for x in self.pk],
            "message": message_str
        })
    
    def prepare_message(self, content, to=None):
        message = {
            "timestamp": str(int(time.time())),
            "content": content,
            "from": self.peer_id,
            "to": self.identify_robot_peer_id(to) 
        }
        return message

    def publish_config(self, config):
        message = self.prepare_message({
            "type": "UpdateConfig",
            "config": config,
        })
        self.send_signed_message(message)
    
    def send_job_message(self, robot_peer_id, job_id, content):
        message = self.prepare_message({
            "type": "JobMessage",
            "job_id": job_id,
            "content": content
        }, robot_peer_id)
        self.send_signed_message(message)

    def start_tunnel_to_job(self, robot_peer_id, job_id, self_peer_id):
        self.start_receiving()
        self.robot_peer_id = robot_peer_id
        self.job_id = job_id
        self.self_peer_id = self_peer_id
        
        message = self.prepare_message({
                "type": "StartTunnelReq",
                "job_id": job_id,
                "peer_id": self_peer_id
        }, robot_peer_id)
        self.send_signed_message(message) 

    def send_terminal_command(self, command):
        self.send_job_message(self.robot_peer_id, self.job_id,
            { 
                "type": "Terminal",
                "stdin": command 
            })
    def start_job(self, robot_peer_id, job_id, job_type, job_args):
        message = self.prepare_message({
            "type": "StartJob",
            "id": job_id,
            "robot_id": robot_peer_id,
            "job_type": job_type,#"docker-container-launch",
            "status": "pending",
            "args": json.dumps(job_args)
        }, robot_peer_id)
        self.send_signed_message(message)
    
    def message_request(self, request_type, request_data, robot_peer_id):
        self.start_receiving()
        self.wait_message = True
        message_response = MessageResponse()
        peer_id = self.identify_robot_peer_id(robot_peer_id)
        @self.subscribe()
        def got_message(message):
            content = message.get('content')
            if message.get('from')!=peer_id:
                return
            if content.get('response_type')==request_type:
                message_response.data = message['content']
                self.wait_message = False
        message = self.prepare_message({
            "type": "MessageRequest",
            "request_type": request_type,
            **request_data
        }, robot_peer_id)
        self.send_signed_message(message)
        self.wait()
        return message_response.data
    
    def custom_message(self, message, robot_peer_id):
       msg = self.prepare_message({
           "type": "CustomMessage",
           **message
       }, robot_peer_id) 
       self.send_signed_message(msg)



    def list_jobs(self, robot_peer_id):
        jobs = self.message_request("ListJobs",{}, robot_peer_id)['jobs']
        return jobs
    
    def get_config(self):
        data = self.send_request('/config', action_param = self.OWNER_KEY)
        if data.get('ok')==False:
            return {"robots": [], "users": [], "version": 0}
        
        return data

        
    def get_nework_info(self):
        data = self.send_request('/network_info', action_param = self.OWNER_KEY)
        if data.get('ok')==False:
            return {}
        
        return data
    
 
    def get_robots(self):
        data = self.get_config()
        network_info = self.get_nework_info()
        print('network', network_info)
        robots = data.get('robots', [])
        for i in range(len(robots)):
            peer_id = robots[i]['robot_peer_id']
            robots[i]['status'] = 'Online' if network_info.get(peer_id, {}).get('is_online') else 'Unknown'
        return robots
 

    def start_terminal_session(self, robot_peer_id:str, job_id: str):

        peer_id = self.identify_robot_peer_id(robot_peer_id)
        @self.subscribe()
        def got_message(message):
            content = message.get('content') or {}
            if message.get('from')!=peer_id:
                return
            
            if content.get('type')=='TunnelResponseMessage' and 'message' in content:
                message = content['message']
                if self.channel_mode=='Terminal':
                    content = message.get('TerminalMessage')
                    if content not in ['\x1b[6n', None]:
                        sys.stdout.write(content)
                        sys.stdout.flush()

        self.channel_mode = "Terminal"

        config = self.send_request("/config", action_param = self.OWNER_KEY)
        self.start_tunnel_to_job(robot_peer_id, job_id, self.peer_id)

        print("===TERMINAL SESSION STARTED===")
        signal.signal(signal.SIGINT, handler)
        time.sleep(1)
        self.send_terminal_command('\n\r')
        self.start_terminal_sender()
        time.sleep(0.1)
        while True:
            key = readchar.readchar()
            # check Crtl+D
            if key in ['\x04']:
                print('===EXIT TERMINAL SESSION===')
                exit(0)
            self.terminal_messages_queue.append(key)
            #self.send_terminal_command(key)




def main():
    start_terminal_session('12D3KooWKiQrCdM7uvs39xcksfU13f68zwYpTJB5b4KwVhXsov7Y', '66a7d0f5a5e85e40e4e89508')

if __name__=='__main__':
    main()