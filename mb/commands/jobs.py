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
from rich.table import Table
from mb.agent import Agent
from mb.settings import AGENT_RPC, USER_KEY_PATH, OWNER_KEY, AGENT_SOCKET_PATH
import uuid

agent_app = typer.Typer()

console = Console()


@agent_app.command()
def add(args_path, robot_peer_id):
    # TODO: send jobs to lot of robots
    agent = Agent(USER_KEY_PATH, AGENT_RPC, AGENT_SOCKET_PATH, OWNER_KEY)
    args = json.load(open(args_path, 'r'))
    job_id = str(uuid.uuid4())
    agent.start_job(robot_peer_id, job_id, 'docker-container-launch', args)
    print("Preparing job: ", job_id)
    print("Requests sent")

@agent_app.command()
def list(robot_peer_id):
    agent = Agent(USER_KEY_PATH, AGENT_RPC, AGENT_SOCKET_PATH, OWNER_KEY)

    jobs = agent.list_jobs(robot_peer_id)
    table = Table("Job Id", "Job Type", "Status")
    for job in jobs:
        table.add_row(job['job_id'], job['job_type'], job['status'])
    print(table)

@agent_app.command()
def terminal(robot_peer_id, job_id):
    agent = Agent(USER_KEY_PATH, AGENT_RPC, AGENT_SOCKET_PATH, OWNER_KEY)
    agent.start_terminal_session(robot_peer_id, job_id)

# @app.command()
# def cp(source_path: str, job_path: str):
#     job_id, dest_path = job_path.split(':')

#     job = requests.post(API_URL + '/jobs.get', json={'organizationId': ORGANIZATION_ID, 'robotJobId': job_id}, headers={'authorization': API_TOKEN}).json()
#     api_key = requests.post(API_URL + '/robots.get', json={'organizationId': ORGANIZATION_ID, 'robotId': job['robot_id']}, headers={'authorization': API_TOKEN}).json()['api_key']

#     files_to_copy = []
#     if os.path.isfile(source_path):
#         arcname = os.path.basename(source_path)
#         files_to_copy.append([source_path, arcname])
#     for root, dirs, files in os.walk(source_path):
#         for file in files:
#             file_path = os.path.join(root, file)
#             arcname = os.path.relpath(file_path, source_path)
#             files_to_copy.append([file_path, arcname])
#     print(files_to_copy) 
#     memory_file = io.BytesIO()
#     with tarfile.open(fileobj=memory_file, mode="w:gz") as tar:
#         for file_path, arcname in files_to_copy:
#             tar.add(file_path, arcname)
#     memory_file.seek(0)
#     data = memory_file.getvalue()
#     print(f"Files are going to be sent. Size: {len(data)} bytes")
#     encoded_data = base64.b64encode(data).decode('utf-8')
#     transfer_tar(api_key, job_id, dest_path, encoded_data)


if __name__ == "__main__":
    agent_app()
