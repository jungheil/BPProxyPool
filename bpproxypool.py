import click

from config import config
from helper.launcher import start_all, start_scheduler, start_server

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=config.common_config["version"])
def cli():
    """ProxyPool cli工具"""


@cli.command(name="schedule")
def schedule():
    """启动调度程序"""
    start_scheduler()


@cli.command(name="server")
def server():
    """启动api服务"""
    start_server()


@cli.command(name="launch")
def launch():
    click.echo(config)
    start_all()


if __name__ == "__main__":
    cli()
