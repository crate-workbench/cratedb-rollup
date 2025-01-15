# Copyright (c) 2021-2025, Crate.io Inc.
# Distributed under the terms of the AGPLv3 license, see LICENSE.

# ruff: noqa: S608
import json
import logging
import os
import time
from uuid import uuid4

import urllib3
from crate import client

from cratedb_toolkit.model import DatabaseAddress

logger = logging.getLogger(__name__)

TRACING = False


last_execution_ts = 0
sys_jobs_log = {}
bucket_list = [10, 50, 100, 500, 1000, 2000, 5000, 10000, 15000, 20000]
bucket_dict = {
    "10": 0,
    "50": 0,
    "100": 0,
    "500": 0,
    "1000": 0,
    "2000": 0,
    "5000": 0,
    "10000": 0,
    "15000": 0,
    "20000": 0,
    "INF": 0,
}

stmt_log_table, last_exec_table, cursor, last_scrape = None, None, None, None


def boot(address: DatabaseAddress):
    # TODO: Refactor to non-global variables.
    global stmt_log_table, last_exec_table, cursor, last_scrape, interval
    schema = address.schema or "stats"

    interval = float(os.getenv("INTERVAL", 10))
    stmt_log_table = os.getenv("STMT_TABLE", f"{schema}.statement_log")
    last_exec_table = os.getenv("LAST_EXEC_TABLE", f"{schema}.last_execution")

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    logger.info(f"Connecting to {address.dburi}")
    conn = client.connect(address.dburi, username=address.username, password=address.password, schema=schema)
    cursor = conn.cursor()
    last_scrape = int(time.time() * 1000) - (interval * 60000)

    dbinit()


def dbinit():
    stmt = (
        f"CREATE TABLE IF NOT EXISTS {stmt_log_table} "
        f"(id TEXT, stmt TEXT, calls INT, bucket OBJECT, last_used TIMESTAMP, "
        f"username TEXT, query_type TEXT, avg_duration FLOAT, nodes ARRAY(TEXT))"
    )
    cursor.execute(stmt)
    stmt = f"SELECT id, stmt, calls, bucket, username, query_type, avg_duration, nodes, last_used FROM {stmt_log_table}"
    cursor.execute(stmt)
    init_stmts(cursor.fetchall())
    stmt = f"CREATE TABLE IF NOT EXISTS {last_exec_table} (last_execution TIMESTAMP)"
    cursor.execute(stmt)
    stmt = f"SELECT last_execution FROM {last_exec_table}"
    cursor.execute(stmt)
    init_last_execution(cursor.fetchall())


def init_last_execution(last_execution):
    global last_execution_ts
    if len(last_execution) == 0:
        last_execution_ts = 0
        stmt = f"INSERT INTO {last_exec_table} (last_execution) VALUES (?)"
        cursor.execute(stmt, (0,))
    else:
        last_execution_ts = last_execution[0][0]


def init_stmts(stmts):
    for stmt in stmts:
        stmt_id = stmt[0]
        stmt_column = stmt[1]
        calls = stmt[2]
        bucket = stmt[3]
        user = stmt[4]
        stmt_type = stmt[5]
        avg_duration = stmt[6]
        nodes = stmt[7]
        last_used = stmt[8]

        if stmt_column not in sys_jobs_log:
            sys_jobs_log[stmt_column] = {
                "id": stmt_id,
                "size": 0,
                "info": [],
                "calls": calls,
                "bucket": bucket,
                "user": user,
                "type": stmt_type,
                "avg_duration": avg_duration,
                "nodes": nodes,
                "last_used": last_used,
                "in_db": True,
                "changed": False,
            }


def write_stats_to_db():
    logger.info(f"Writing statistics to database table: {stmt_log_table}")
    write_query_stmt = (
        f"INSERT INTO {stmt_log_table} "
        f"(id, stmt, calls, bucket, username, query_type, avg_duration, nodes, last_used) "
        f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    update_query_stmt = (
        f"UPDATE {stmt_log_table} SET calls = ?, avg_duration = ?, nodes = ?, bucket = ?, last_used = ? WHERE id = ?"
    )
    write_params = []
    for key in sys_jobs_log.keys():
        if not sys_jobs_log[key]["in_db"]:
            write_params.append(
                [
                    sys_jobs_log[key]["id"],
                    key,
                    sys_jobs_log[key]["calls"],
                    sys_jobs_log[key]["bucket"],
                    sys_jobs_log[key]["user"],
                    sys_jobs_log[key]["type"],
                    sys_jobs_log[key]["avg_duration"],
                    sys_jobs_log[key]["nodes"],
                    sys_jobs_log[key]["last_used"],
                ]
            )
            sys_jobs_log[key]["in_db"] = True
            sys_jobs_log[key]["changed"] = False
        elif sys_jobs_log[key]["changed"]:
            cursor.execute(
                update_query_stmt,
                (
                    sys_jobs_log[key]["calls"],
                    sys_jobs_log[key]["avg_duration"],
                    sys_jobs_log[key]["nodes"],
                    sys_jobs_log[key]["bucket"],
                    sys_jobs_log[key]["last_used"],
                    sys_jobs_log[key]["id"],
                ),
            )
            sys_jobs_log[key]["changed"] = False
    if len(write_params) > 0:
        cursor.executemany(write_query_stmt, write_params)

    stmt = f"UPDATE {last_exec_table} SET last_execution = ?"
    cursor.execute(stmt, (last_scrape,))


def read_stats():
    stmt = (
        f"SELECT id, stmt, calls, avg_duration, bucket, username, query_type, nodes, last_used "
        f"FROM {stmt_log_table} ORDER BY calls DESC, avg_duration DESC;"
    )
    cursor.execute(stmt)
    init_stmts(cursor.fetchall())
    return sys_jobs_log


def assign_to_bucket(bucket, duration):
    found = False
    for element in bucket_list:
        if duration < element:
            found = True
            bucket[str(element)] += 1
            break
    if not found:
        bucket["INF"] += 1

    return bucket


def update_statistics(query_results):
    global sys_jobs_log
    for result in query_results:
        started = result[0]
        ended = result[1]
        classification = result[2]
        stmt = result[3]
        user = result[4]
        node = json.dumps(result[5])

        duration = ended - started
        if stmt not in sys_jobs_log:
            sys_jobs_log[stmt] = {
                "id": str(uuid4()),
                "calls": 0,
                "bucket": dict(bucket_dict),
                "user": user,
                "type": classification["type"],
                "avg_duration": duration,
                "in_db": False,
                "last_used": started,
                "nodes": [],
                "changed": True,
            }
        sys_jobs_log[stmt]["changed"] = True
        sys_jobs_log[stmt]["avg_duration"] = (sys_jobs_log[stmt]["avg_duration"] + duration) / 2
        sys_jobs_log[stmt]["bucket"] = assign_to_bucket(sys_jobs_log[stmt]["bucket"], duration)
        sys_jobs_log[stmt]["last_used"] = started
        sys_jobs_log[stmt]["calls"] += 1
        sys_jobs_log[stmt]["nodes"].append(node)
        sys_jobs_log[stmt]["nodes"] = list(set(sys_jobs_log[stmt]["nodes"]))  # only save unique nodes
    if TRACING:
        logger.info(f"Updated statistics: {sys_jobs_log}")


def scrape_db():
    global last_scrape
    logger.info("Reading sys.jobs_log")
    next_scrape = int(time.time() * 1000)
    stmt = (
        f"SELECT "
        f"started, ended, classification, stmt, username, node "
        f"FROM sys.jobs_log "
        f"WHERE "
        f"stmt NOT LIKE '%sys.%' AND "
        f"stmt NOT LIKE '%information_schema.%' "
        f"AND ended BETWEEN {last_scrape} AND {next_scrape} "
        f"ORDER BY ended DESC"
    )

    cursor.execute(stmt)
    result = cursor.fetchall()
    update_statistics(result)
    last_scrape = next_scrape


def record_once():
    logger.info("Recording information snapshot")
    scrape_db()
    write_stats_to_db()


def record_forever():
    while True:
        record_once()
        logger.info(f"Sleeping for {interval} seconds")
        time.sleep(interval)


def main():
    boot()
    record_forever()


if __name__ == "__main__":
    main()
