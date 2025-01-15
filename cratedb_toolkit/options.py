import click

cratedb_cluster_id_option = click.option(
    "--cluster-id", envvar="CRATEDB_CLOUD_CLUSTER_ID", type=str, required=False, help="CrateDB Cloud cluster identifier"
)
cratedb_sqlalchemy_option = click.option(
    "--cratedb-sqlalchemy-url", envvar="CRATEDB_SQLALCHEMY_URL", type=str, required=False, help="CrateDB SQLAlchemy URL"
)
cratedb_http_option = click.option(
    "--cratedb-http-url", envvar="CRATEDB_HTTP_URL", type=str, required=False, help="CrateDB HTTP URL"
)
