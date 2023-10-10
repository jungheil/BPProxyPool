import click

from config import common_config, get_env
from helper.launcher import start_all, start_scheduler, start_server

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=common_config["version"])
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
    click.echo(common_config["banner"])
    start_all()


if __name__ == "__main__":
    get_env()
    cli()
