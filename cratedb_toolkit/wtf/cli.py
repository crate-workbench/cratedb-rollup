# Copyright (c) 2021-2024, Crate.io Inc.
# Distributed under the terms of the AGPLv3 license, see LICENSE.
import logging
import typing as t

import click
from click import ClickException
from click_aliases import ClickAliasedGroup

from cratedb_toolkit.model import DatabaseAddress
from cratedb_toolkit.options import cratedb_http_option, cratedb_sqlalchemy_option
from cratedb_toolkit.util import DatabaseAdapter
from cratedb_toolkit.util.cli import (
    boot_click,
    make_command,
)
from cratedb_toolkit.util.data import jd
from cratedb_toolkit.wtf.core import InfoContainer, JobInfoContainer, LogContainer
from cratedb_toolkit.wtf.recorder import InfoRecorder

logger = logging.getLogger(__name__)


def help_info():
    """
    Database cluster and system information.

    Synopsis
    ========

    export CRATEDB_SQLALCHEMY_URL=crate://localhost/
    cratedb-wtf info

    """  # noqa: E501


def help_logs():
    """
    Database cluster logs.

    Synopsis
    ========

    export CRATEDB_SQLALCHEMY_URL=crate://localhost/
    cratedb-wtf logs

    """  # noqa: E501


def help_statistics():
    """
    Database cluster job / query statistics.

    Synopsis
    ========

    export CRATEDB_SQLALCHEMY_URL=crate://localhost/
    cratedb-wtf job-statistics quick
    cratedb-wtf job-statistics collect
    cratedb-wtf job-statistics view

    """  # noqa: E501


def help_serve():
    """
    Start HTTP service to expose collected information.

    Synopsis
    ========

    export CRATEDB_SQLALCHEMY_URL=crate://localhost/
    cratedb-wtf serve

    """  # noqa: E501


@click.group(cls=ClickAliasedGroup)  # type: ignore[arg-type]
@cratedb_sqlalchemy_option
@cratedb_http_option
@click.option("--verbose", is_flag=True, required=False, help="Turn on logging")
@click.option("--debug", is_flag=True, required=False, help="Turn on logging with debug level")
@click.option("--scrub", envvar="SCRUB", is_flag=True, required=False, help="Blank out identifiable information")
@click.version_option()
@click.pass_context
def cli(
    ctx: click.Context, cratedb_sqlalchemy_url: str, cratedb_http_url: str, verbose: bool, debug: bool, scrub: bool
):
    """
    Diagnostics and informational utilities.
    """
    if not cratedb_sqlalchemy_url and not cratedb_http_url:
        raise ClickException("Unable to operate without database address")
    ctx.meta.update(
        {"cratedb_http_url": cratedb_http_url, "cratedb_sqlalchemy_url": cratedb_sqlalchemy_url, "scrub": scrub}
    )
    return boot_click(ctx, verbose, debug)


@make_command(cli, "info", help_info)
@click.pass_context
def info(ctx: click.Context):
    cratedb_sqlalchemy_url = ctx.meta["cratedb_sqlalchemy_url"]
    scrub = ctx.meta.get("scrub", False)
    adapter = DatabaseAdapter(dburi=cratedb_sqlalchemy_url)
    sample = InfoContainer(adapter=adapter, scrub=scrub)
    jd(sample.to_dict())


@make_command(cli, "logs", help_logs)
@click.pass_context
def logs(ctx: click.Context):
    cratedb_sqlalchemy_url = ctx.meta["cratedb_sqlalchemy_url"]
    scrub = ctx.meta.get("scrub", False)
    adapter = DatabaseAdapter(dburi=cratedb_sqlalchemy_url)
    sample = LogContainer(adapter=adapter, scrub=scrub)
    jd(sample.to_dict())


@make_command(cli, "job-info", "Display information about jobs / queries.")
@click.pass_context
def job_information(ctx: click.Context):
    """
    Display ad hoc job information.
    """
    cratedb_sqlalchemy_url = ctx.meta["cratedb_sqlalchemy_url"]
    scrub = ctx.meta.get("scrub", False)
    adapter = DatabaseAdapter(dburi=cratedb_sqlalchemy_url)
    sample = JobInfoContainer(adapter=adapter, scrub=scrub)
    jd(sample.to_dict())


@click.group(cls=ClickAliasedGroup)  # type: ignore[arg-type]
@click.pass_context
def job_statistics(ctx: click.Context):
    """
    Collect and display statistics about jobs / queries.
    """
    pass


cli.add_command(job_statistics, name="job-statistics", aliases=["jobstats"])


@make_command(job_statistics, "collect", "Collect queries from sys.jobs_log.")
@click.option("--once", is_flag=True, default=False, required=False, help="Whether to record only one sample")
@click.pass_context
def job_statistics_collect(ctx: click.Context, once: bool):
    """
    Run jobs_log collector.
    """
    import cratedb_toolkit.wtf.query_collector

    address = DatabaseAddress.from_string(ctx.meta["cratedb_http_url"] or ctx.meta["cratedb_sqlalchemy_url"])

    cratedb_toolkit.wtf.query_collector.boot(address=address)
    if once:
        cratedb_toolkit.wtf.query_collector.record_once()
    else:
        cratedb_toolkit.wtf.query_collector.record_forever()


@make_command(job_statistics, "view", "View job statistics about collected queries.")
@click.pass_context
def job_statistics_view(ctx: click.Context):
    """
    View job statistics about collected queries.
    """
    import cratedb_toolkit.wtf.query_collector

    address = DatabaseAddress.from_string(ctx.meta["cratedb_http_url"] or ctx.meta["cratedb_sqlalchemy_url"])
    cratedb_toolkit.wtf.query_collector.boot(address=address)

    response: t.Dict = {"meta": {}, "data": {}}
    response["meta"]["remark"] = "WIP! This is a work in progress. The output format will change."
    response["data"]["stats"] = cratedb_toolkit.wtf.query_collector.read_stats()
    jd(response)


@make_command(cli, "record", "Record `info` and `job-info` outcomes.")
@click.option("--once", is_flag=True, default=False, required=False, help="Whether to record only one sample")
@click.pass_context
def record(ctx: click.Context, once: bool):
    cratedb_sqlalchemy_url = ctx.meta["cratedb_sqlalchemy_url"]
    scrub = ctx.meta.get("scrub", False)
    adapter = DatabaseAdapter(dburi=cratedb_sqlalchemy_url, echo=False)
    recorder = InfoRecorder(adapter=adapter, scrub=scrub)
    if once:
        recorder.record_once()
    else:
        recorder.record_forever()


@make_command(cli, "serve", help_serve)
@click.option("--listen", type=click.STRING, default=None, help="HTTP server listen address")
@click.option("--reload", is_flag=True, help="Dynamically reload changed files")
@click.pass_context
def serve(ctx: click.Context, listen: str, reload: bool):
    from cratedb_toolkit.wtf.http import start

    start(listen, reload=reload)
