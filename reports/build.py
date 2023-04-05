import typer

app = typer.Typer()


@app.command()
def generate_parameters():
    generate_index_report.main()


if __name__ == "__main__":
    app()
