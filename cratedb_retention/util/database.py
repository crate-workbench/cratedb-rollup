# Copyright (c) 2023, Crate.io Inc.
# Distributed under the terms of the AGPLv3 license, see LICENSE.
import sqlalchemy as sa


def run_sql(dburi: str, sql: str, records: bool = False):
    return DatabaseAdapter(dburi=dburi).run_sql(sql=sql, records=records)


class DatabaseAdapter:
    """
    Wrap SQLAlchemy connection to database.
    """

    def __init__(self, dburi: str):
        self.dburi = dburi
        self.engine = sa.create_engine(self.dburi, echo=False)
        self.connection = self.engine.connect()

    def run_sql(self, sql: str, records: bool = False, ignore: str = None):
        """
        Run SQL statement, and return results, optionally ignoring exceptions.
        """
        try:
            return self.run_sql_real(sql=sql, records=records)
        except Exception as ex:
            if not ignore:
                raise
            if ignore not in str(ex):
                raise

    def run_sql_real(self, sql: str, records: bool = False):
        """
        Invoke SQL statement, and return results.
        """
        result = self.connection.execute(sa.text(sql))
        if records:
            rows = result.mappings().fetchall()
            return [dict(row.items()) for row in rows]
        else:
            return result.fetchall()

    def count_records(self, tablename_full: str):
        """
        Return number of records in table.
        """
        sql = f"SELECT COUNT(*) AS count FROM {tablename_full};"  # noqa: S608
        results = self.run_sql(sql=sql)
        return results[0][0]
