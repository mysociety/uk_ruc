import rich_click as click
from .create_unified_measure import create_composite_measure


@click.group()
def cli():
    pass


def main():
    cli()


@cli.command()
def build():
    create_composite_measure()


if __name__ == "__main__":
    main()
