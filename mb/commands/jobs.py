import typer
import json
import requests
import os
import io
import tarfile
import base64
from rich import print
from rich.console import Console
from rich.table import Table
from mb.settings import API_URL, API_TOKEN, ORGANIZATION_ID, AGENT_SOCKET_PATH
from mb.client import start_terminal_session, transfer_tar
from mb.agent import Agent
import uuid

app = typer.Typer()
agent_app = typer.Typer()

console = Console()


@agent_app.command()
def add(args_path, robot_peer_id):
    # TODO: send jobs to lot of robots
    agent = Agent(AGENT_SOCKET_PATH)
    args = json.load(open(args_path, 'r'))
    job_id = str(uuid.uuid4())
    agent.start_job(robot_peer_id, job_id, 'docker-container-launch', args)
    print("Preparing job: ", job_id)
    print("Requests sent")

@agent_app.command()
def terminal(robot_peer_id, job_id):
    agent = Agent(AGENT_SOCKET_PATH)
    agent.start_terminal_session(robot_peer_id, job_id)

@app.command()
def add(args_path: str, robot_ids: str):
    robot_ids = robot_ids.split(',')
    res = requests.post(API_URL + '/robots.addJobs', json={
        "organizationId": ORGANIZATION_ID,
        "robotIds": robot_ids,
        "job_type": "docker-container-launch",  
        "args": json.load(open(args_path, 'r'))
        }, headers={'authorization': API_TOKEN}).json()
    print(res)

@app.command()
def get(job_id):
    job = requests.post(API_URL + '/jobs.get', json={'organizationId': ORGANIZATION_ID, 'robotJobId': job_id}, headers={'authorization': API_TOKEN}).json()

    print(job)

@app.command()
def terminal(job_id: str):
    job = requests.post(API_URL + '/jobs.get', json={'organizationId': ORGANIZATION_ID, 'robotJobId': job_id}, headers={'authorization': API_TOKEN}).json()
    api_key = requests.post(API_URL + '/robots.get', json={'organizationId': ORGANIZATION_ID, 'robotId': job['robot_id']}, headers={'authorization': API_TOKEN}).json()['api_key']
    start_terminal_session(api_key, job_id) 
@app.command()
def cp(source_path: str, job_path: str):
    job_id, dest_path = job_path.split(':')
    
    job = requests.post(API_URL + '/jobs.get', json={'organizationId': ORGANIZATION_ID, 'robotJobId': job_id}, headers={'authorization': API_TOKEN}).json()
    api_key = requests.post(API_URL + '/robots.get', json={'organizationId': ORGANIZATION_ID, 'robotId': job['robot_id']}, headers={'authorization': API_TOKEN}).json()['api_key']

    files_to_copy = []
    if os.path.isfile(source_path):
        arcname = os.path.basename(source_path)
        files_to_copy.append([source_path, arcname])
    for root, dirs, files in os.walk(source_path):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, source_path)
            files_to_copy.append([file_path, arcname])
    print(files_to_copy) 
    memory_file = io.BytesIO()
    with tarfile.open(fileobj=memory_file, mode="w:gz") as tar:
        for file_path, arcname in files_to_copy:
            tar.add(file_path, arcname)
    memory_file.seek(0)
    data = memory_file.getvalue()
    print(f"Files are going to be sent. Size: {len(data)} bytes")
    encoded_data = base64.b64encode(data).decode('utf-8')
    transfer_tar(api_key, job_id, dest_path, encoded_data)
    
if __name__ == "__main__":
    app()
