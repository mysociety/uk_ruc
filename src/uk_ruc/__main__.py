import rich_click as click
from .create_unified_measure import create_composite_measure
from .create_la_data import generate_la_data


def create_files():
    create_composite_measure()
    generate_la_data()


@click.group()
def cli():
    pass


def main():
    cli()


@cli.command()
def build():
    create_files()


if __name__ == "__main__":
    main()
