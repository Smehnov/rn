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
import uuid

agent_app = typer.Typer()

console = Console()


@agent_app.command()
def add(args_path, robot_peer_id):
    # TODO: send jobs to lot of robots
    agent = Agent()
    args = json.load(open(args_path, 'r'))
    job_id = str(uuid.uuid4())
    agent.start_job(robot_peer_id, job_id, 'docker-container-launch', args)
    print("Preparing job: ", job_id)
    print("Requests sent")

@agent_app.command()
def list(robot_peer_id):
    agent = Agent()
    jobs = agent.list_jobs(robot_peer_id)
    table = Table("Job Id", "Job Type", "Status")
    for job in jobs:
        table.add_row(job['job_id'], job['job_type'], job['status'])
    print(table)

@agent_app.command()
def terminal(robot_peer_id, job_id):
    agent = Agent()
    agent.start_terminal_session(robot_peer_id, job_id)

if __name__ == "__main__":
    agent_app()
