import typer
import requests
from rich import print
from rich.console import Console
from rich.table import Table
from mb.agent import Agent
from mb.settings import API_URL, API_TOKEN, ORGANIZATION_ID, AGENT_SOCKET_PATH


app = typer.Typer()
agent_app = typer.Typer()

console = Console()


@agent_app.command()
def list():
    agent = Agent(AGENT_SOCKET_PATH) 
    robots = agent.get_robots()
    table = Table("PeerId", "Name", "Status")
    for robot in robots:
        table.add_row(robot['robot_peer_id'], robot['name'], 'Unknown')
    console.print(table)
   

@app.command()
def list():
    res = requests.post(API_URL + '/robots.list', json={'organizationId': ORGANIZATION_ID}, headers={'authorization': API_TOKEN}).json()
    table = Table("Id", "Name", "Description", "Status", 'Api Key')
    for robot in res['robots']:
        table.add_row(robot['id'], robot['name'], robot['description'], robot['status'], robot['api_key'])
    console.print(table)

@app.command()
def get(robot_id: str):
    robot = requests.post(API_URL + '/robots.get', json={'organizationId': ORGANIZATION_ID, 'robotId': robot_id}, headers={'authorization': API_TOKEN}).json()
    print(robot)

if __name__ == "__main__":
    app()
