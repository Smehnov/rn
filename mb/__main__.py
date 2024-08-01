import typer
from mb.commands import robots, jobs
from mb.settings import AGENT_SOCKET_PATH

app = typer.Typer()
if AGENT_SOCKET_PATH:
    app.add_typer(jobs.agent_app, name="jobs")
else:
    app.add_typer(robots.app, name="robots")
    app.add_typer(jobs.app, name="jobs")

def main():
    app()

if __name__ == "__main__":
    main()
