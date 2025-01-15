# Changelog

## Unreleased
- Fixed connectivity for `job-statistics collect`

## 2025/01/13 v0.0.30
- Dependencies: Minimize dependencies of core installation,
  defer `polars` to `cratedb-toolkit[io]`.
- Fixed `cratedb-wtf record` about too large values of `ulimit_hard`
- Improved `ctk shell` to also talk to CrateDB standalone databases
- Added basic utility command `ctk tail`, for tailing a database
  table, and optionally following the tail
- Table Loader: Added capability to load InfluxDB Line Protocol (ILP) files
- Query Collector: Now respects `CRATEDB_SQLALCHEMY_URL` environment variable

## 2024/10/13 v0.0.29
- MongoDB: Added Zyp transformations to the CDC subsystem,
  making it more symmetric to the full-load procedure.
- Query Converter: Added very basic expression converter utility with
  CLI interface
- DynamoDB: Added query expression converter for relocating object
  references, to support query migrations after the breaking change
  with the SQL DDL schema, by v0.0.27.

## 2024/10/09 v0.0.28
- IO: Improved `BulkProcessor` when running per-record operations by
  also checking `rowcount` for handling `INSERT OK, 0 rows` responses
- MongoDB: Fixed BSON decoding of `{"$date": 1180690093000}` timestamps
  by updating to commons-codec 0.0.21.
- Testcontainers: Don't always pull the OCI image before starting.
  It is unfortunate in disconnected situations.

## 2024/10/01 v0.0.27
- MongoDB: Updated to pymongo 4.9
- DynamoDB: Change CrateDB data model to use (`pk`, `data`, `aux`) columns
  Attention: This is a breaking change.

## 2024/09/26 v0.0.26
- MongoDB: Configure `MongoDBCrateDBConverter` after updating to commons-codec 0.0.18
- DynamoDB CDC: Fix `MODIFY` operation to also propagate deleted attributes

## 2024/09/22 v0.0.25
- Table Loader: Improved conditional handling of "transformation" parameter
- Table Loader: Improved status reporting and error logging in `BulkProcessor`
- MongoDB: Improve error reporting
- MongoDB Full: Polars' `read_ndjson` doesn't load MongoDB JSON data well,
  use `fsspec` and `orjson` instead
- MongoDB Full: Improved initialization of transformation subsystem
- MongoDB Adapter: Improved performance of when computing collection cardinality
  by using `collection.estimated_document_count()`
- MongoDB Full: Optionally use `limit` parameter as number of total records
- MongoDB Adapter: Evaluate `_id` filter field by upcasting to `bson.ObjectId`,
  to convey a filter that makes `ctk load table` process a single document,
  identified by its OID
- MongoDB Dependencies: Update to commons-codec 0.0.17

## 2024/09/19 v0.0.24
- MongoDB Full: Refactor transformation subsystem to `commons-codec`
- MongoDB: Update to commons-codec v0.0.16

## 2024/09/16 v0.0.23
- MongoDB: Unlock processing multiple collections, either from server database,
  or from filesystem directory
- MongoDB: Unlock processing JSON files from HTTP resource, using `https+bson://`
- MongoDB: Optionally filter server collection using MongoDB query expression
- MongoDB: Improve error handling wrt. bulk operations vs. usability
- DynamoDB CDC: Add `ctk load table` interface for processing CDC events
- DynamoDB CDC: Accept a few more options for the Kinesis Stream:
  batch-size, create, create-shards, start, seqno, idle-sleep, buffer-time
- DynamoDB Full: Improve error handling wrt. bulk operations vs. usability

## 2024/09/10 v0.0.22
- MongoDB: Rename columns with leading underscores to use double leading underscores
- MongoDB: Add support for UUID types
- MongoDB: Improve reading timestamps in previous BSON formats
- MongoDB: Fix processing empty arrays/lists. By default, assume `TEXT` as inner type.
- MongoDB: For `ctk load table`, use "partial" scan for inferring the collection schema,
  based on the first 10,000 documents.
- MongoDB: Skip leaking `UNKNOWN` fields into SQL DDL.
  This means relevant column definitions will not be included into the SQL DDL.
- MongoDB: Make `ctk load table` use the `data OBJECT(DYNAMIC)` mapping strategy.
- MongoDB: Sanitize lists of varying objects
- MongoDB: Add treatment option for applying special treatments to certain items
  on real-world data
- MongoDB: Use pagination on source collection, for creating batches towards CrateDB
- MongoDB: Unlock importing MongoDB Extended JSON files using `file+bson://...`

## 2024/09/02 v0.0.21
- DynamoDB: Add special decoding for varied lists.
  Store them into a separate `OBJECT(IGNORED)` column in CrateDB.
- DynamoDB: Add pagination support for `full-load` table loader

## 2024/08/27 v0.0.20
- DMS/DynamoDB: Fix table name quoting within CDC processor handler

## 2024/08/26 v0.0.19
- MongoDB: Fix and verify Zyp transformations
- DMS/DynamoDB/MongoDB I/O: Use SQL with parameters instead of inlining values

## 2024/08/21 v0.0.18
- Dependencies: Unpin commons-codec, to always use the latest version
- Dependencies: Unpin lorrystream, to always use the latest version
- MongoDB: Improve type mapper by discriminating between
  `INTEGER` and `BIGINT`
- MongoDB: Improve type mapper by supporting BSON `DatetimeMS`,
  `Decimal128`, and `Int64` types

## 2024/08/19 v0.0.17
- Processor: Updated Kinesis Lambda processor to understand AWS DMS
- MongoDB: Fix missing output on STDOUT for `migr8 export`
- MongoDB: Improve timestamp parsing by using `python-dateutil`
- MongoDB: Converge `_id` input field to `id` column instead of dropping it
- MongoDB: Make user interface use stderr, so stdout is for data only
- MongoDB: Make `migr8 extract` write to stdout by default
- MongoDB: Make `migr8 translate` read from stdin by default
- MongoDB: Improve user interface messages
- MongoDB: Strip single leading underscore character from all top-level fields
- MongoDB: Map OID types to CrateDB TEXT columns
- MongoDB: Make `migr8 extract` and `migr8 export` accept the `--limit` option
- MongoDB: Fix indentation in prettified SQL output of `migr8 translate`
- MongoDB: Add capability to give type hints and add transformations
- Dependencies: Adjust code for lorrystream version 0.0.3
- Dependencies: Update to lorrystream 0.0.4 and commons-codec 0.0.7
- DynamoDB: Add table loader for full-load operations

## 2024/07/25 v0.0.16
- `ctk load table`: Added support for MongoDB Change Streams
- Fix dependency with the `kaggle` package, downgrade to `kaggle==1.6.14`
- DynamoDB CDC: Add demo to support reading DynamoDB change data capture

## 2024/07/08 v0.0.15
- IO: Added the `if-exists` query parameter by updating to influxio 0.4.0.
- Rockset: Added CrateDB Rockset Adapter, a HTTP API emulation layer
- MongoDB: Added adapter amalgamating PyMongo to use CrateDB as backend
- SQLAlchemy: Clean up and refactor SQLAlchemy polyfills
  to `cratedb_toolkit.util.sqlalchemy`
- CFR: Build as a self-contained program using PyInstaller
- CFR: Publish self-contained application bundle to GitHub Workflow Artifacts

## 2024/06/18 v0.0.14
- Add `ctk cfr` and `ctk wtf` diagnostics programs
- Remove support for Python 3.7
- SQLAlchemy dialect: Use `sqlalchemy-cratedb>=0.37.0`
  This includes the fix to the `get_table_names()` reflection method.

## 2024/06/11 v0.0.13
- Dependencies: Migrate from `crate[sqlalchemy]` to `sqlalchemy-cratedb`

## 2024/05/30 v0.0.12
- Fix InfluxDB Cloud <-> CrateDB Cloud connectivity by using
  `ssl=true` query argument also for `influxdb2://` source URLs.

## 2024/05/30 v0.0.11
- Fix InfluxDB Cloud <-> CrateDB Cloud connectivity by propagating
  `ssl=true` query argument. Update dependencies to `influxio>=0.2.1,<1`.

## 2024/04/10 v0.0.10
- Dependencies: Unpin upper version bound of `dask`. Otherwise, compatibility
  issues can not be resolved quickly, like with Python 3.11.9.
  https://github.com/dask/dask/issues/11038

## 2024/03/22 v0.0.9
- Dependencies: Use `dask[dataframe]`

## 2024/03/11 v0.0.8
- datasets: Fix compatibility with Python 3.7

## 2024/03/07 v0.0.7
- datasets: Fix dataset loader

## 2024/03/07 v0.0.6

- Added `cratedb_toolkit.datasets` subsystem, for acquiring datasets
  from cratedb-datasets and Kaggle.


## 2024/02/12 v0.0.5

- Do not always activate pytest11 entrypoint to pytest fixture
  `cratedb_service`, as it depends on the `testcontainers` package,
  which is not always installed.


## 2024/02/10 v0.0.4

- Packaging: Use `cloud` extra to install relevant packages
- Dependencies: Add `testing` extra, which installs `testcontainers` only
- Testing: Export `cratedb_service` fixture as pytest11 entrypoint
- Sandbox: Reduce number of extras by just using `all`


## 2024/01/18 v0.0.3

- Add SQL runner utility primitives to `io.sql` namespace
- Add `import_csv_pandas` and `import_csv_dask` utility primitives
- data: Add subsystem for "loading" data.
- Add SDK and CLI for CrateDB Cloud Data Import APIs
  `ctk load table ...`
- Add `migr8` program from previous repository
- InfluxDB: Add adapter for `influxio`
- MongoDB: Add `migr8` program from previous repository
- MongoDB: Improve UX by using `ctk load table mongodb://...`
- load table: Refactor to use more OO
- Add `examples/cloud_import.py`
- Adapt testcontainers to be agnostic of the testing framework.
  Thanks, @pilosus.


## 2023/11/06 v0.0.2

- CLI: Upgrade to `click-aliases>=1.0.2`, fixing erroring out when no group aliases
  are specified.

- Add support for Python 3.12

- SQLAlchemy: Improve UNIQUE constraints polyfill to accept multiple
  column names, for emulating unique composite keys.


## 2023/10/10 v0.0.1

- SQLAlchemy: Add a few patches and polyfills, which do not fit well
  into the vanilla Python driver / SQLAlchemy dialect.

- Retention: Refactor strategies `delete`, `reallocate`, and `snapshot`, to
  standalone variants.

- Retention: Bundle configuration and runtime settings into `Settings` entity,
  and use more OO instead of weak dictionaries: Add `RetentionStrategy`,
  `TableAddress`, and `Settings` entities, to improve information passing
  throughout the application and the SQL templates.

- Retention: Add `--schema` option, and `CRATEDB_EXT_SCHEMA` environment variable,
  to configure the database schema used to store the retention policy
  table. The default value is `ext`.

- Retention: Use full-qualified table names everywhere.

- Retention: Fix: Compensate for `DROP REPOSITORY` now returning `RepositoryMissingException`
  when the repository does not exist. With previous versions of CrateDB, it was
  `RepositoryUnknownException`.


## 2023/06/27 v0.0.0

- Import "data retention" implementation from <https://github.com/crate/crate-airflow-tutorial>.
  Thanks, @hammerhead.
