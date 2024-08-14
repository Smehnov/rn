import typer
from mb.tui.tuiapp import start



agent_app = typer.Typer()


@agent_app.command()
def config(config_path):
    start(config_path)


