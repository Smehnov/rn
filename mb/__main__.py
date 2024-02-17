import typer
from mb.commands import robots, jobs


app = typer.Typer()
app.add_typer(robots.app, name="robot")
app.add_typer(jobs.app, name="job")


if __name__ == "__main__":
    app()
