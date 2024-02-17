import typer
import requests
from rich import print
from rich.console import Console
from rich.table import Table
from mb.settings import API_URL, API_TOKEN, ORGANIZATION_ID


app = typer.Typer()

console = Console()


@app.command()
def list():
    res = requests.post(API_URL + '/robots.list', json={'organizationId': ORGANIZATION_ID}, headers={'authorization': API_TOKEN}).json()
    table = Table("Id", "Name", "Description", "Status", 'Api Key')
    for robot in res['robots']:
        table.add_row(robot['id'], robot['name'], robot['description'], robot['status'], robot['api_key'])
    console.print(table)


if __name__ == "__main__":
    app()
