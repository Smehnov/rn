import typer
from mb.commands import robots, jobs, keys, tui
from mb.settings import AGENT_SOCKET_PATH

app = typer.Typer()
if AGENT_SOCKET_PATH:
    app.add_typer(jobs.agent_app, name="jobs")
    app.add_typer(robots.agent_app, name="robots")
    app.add_typer(keys.agent_app, name="keys")
    app.add_typer(tui.agent_app, name="tui")
else:
    app.add_typer(robots.app, name="robots")
    app.add_typer(jobs.app, name="jobs")

def main():
    app()

if __name__ == "__main__":
    main()
