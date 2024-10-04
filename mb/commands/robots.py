import typer
import requests
from rich import print
from rich.console import Console
from rich.table import Table
from mb.agent import Agent
import time


app = typer.Typer()
agent_app = typer.Typer()

console = Console()


@agent_app.command()
def list():
    agent = Agent()
    robots = agent.get_robots()
    table = Table("PeerId", "Name", "Status")
    for robot in robots:
        table.add_row(robot['robot_peer_id'], robot['name'], robot['status']) 
    console.print(table)

@agent_app.command()
def echo(robot_peer_id:str, message: str):
    agent = Agent()
    for i in range(100):
        agent.custom_message({'msg': message}, robot_peer_id)
   
@agent_app.command()
def listen():
    agent = Agent()
    @agent.subscribe()
    def got_message(message):
        print(message)
    agent.start_receiving()
    while True:
        time.sleep(1) 

if __name__ == "__main__":
    agent_app()
