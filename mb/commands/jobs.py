import typer
import json
import requests
from rich import print
from rich.console import Console
from rich.table import Table
from settings import API_URL, API_TOKEN, ORGANIZATION_ID


app = typer.Typer()

console = Console()


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

if __name__ == "__main__":
    app()
