import typer
from mb.commands import robots, jobs, keys, tui
from mb.settings import AGENT_SOCKET_PATH

app = typer.Typer()
app.add_typer(jobs.agent_app, name="jobs")
app.add_typer(robots.agent_app, name="robots")
app.add_typer(keys.agent_app, name="keys")
app.add_typer(tui.agent_app, name="tui")

def main():
    app()

if __name__ == "__main__":
    main()
