import typer
import requests
from rich import print
from rich.console import Console
from rich.table import Table
from mb.agent import Agent
from mb.settings import AGENT_SOCKET_PATH


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
   
if __name__ == "__main__":
    agent_app()
