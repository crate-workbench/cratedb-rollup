import dataclasses
import typing as t
from copy import deepcopy
from urllib.parse import urljoin

from attr import Factory
from attrs import define
from boltons.urlutils import URL


@dataclasses.dataclass
class DatabaseAddress:
    """
    Manage a database address, which is either a SQLAlchemy-
    compatible database URI, or a regular HTTP URL.
    """

    uri: URL

    @classmethod
    def from_string(cls, url):
        """
        Factory method to create an instance from an SQLAlchemy database URL in string format.
        """
        return cls(uri=URL(url))

    @classmethod
    def from_httpuri(cls, url):
        """
        Factory method to create an instance from an HTTP URL in string format.
        """
        uri = URL(url)
        if uri.scheme == "https":
            uri.query_params["ssl"] = "true"
        uri.scheme = "crate"
        return cls(uri=uri)

    @property
    def dburi(self) -> str:
        """
        Return a string representation of the database URI.
        """
        return str(self.uri)

    @property
    def httpuri(self) -> str:
        """
        Return the `http(s)://` variant of the database URI.
        """
        uri = deepcopy(self.uri)
        uri.scheme = "http"
        if "ssl" in uri.query_params:
            if uri.query_params["ssl"]:
                uri.scheme = "https"
            del uri.query_params["ssl"]
        return str(uri)

    @property
    def safe(self):
        """
        Return a string representation of the database URI, safe for printing.
        The password is stripped from the URL, and replaced by `REDACTED`.
        """
        uri = deepcopy(self.uri)
        uri.password = "REDACTED"  # noqa: S105
        return str(uri)

    def decode(self) -> t.Tuple[URL, "TableAddress"]:
        """
        Decode database and table names, and sanitize database URI.
        """
        from cratedb_toolkit.util.database import decode_database_table

        database, table = decode_database_table(self.dburi)
        uri = deepcopy(self.uri)
        if not uri.scheme.startswith("file"):
            uri.path = ""
        return uri, TableAddress(database, table)

    @property
    def username(self) -> t.Union[str, None]:
        """
        Return the username of the database URI.
        """
        return self.uri.username

    @property
    def password(self) -> t.Union[str, None]:
        """
        Return the password of the database URI.
        """
        return self.uri.password

    @property
    def schema(self) -> t.Union[str, None]:
        """
        Return the `?schema=` query parameter of the database URI.
        """
        return self.uri.query_params.get("schema")


@dataclasses.dataclass
class TableAddress:
    """
    Manage a table address, which is made of "<schema>"."<table>".
    """

    schema: t.Optional[str] = None
    table: t.Optional[str] = None

    @property
    def fullname(self):
        """
        Return a full-qualified quoted table identifier.
        """
        from cratedb_toolkit.util import DatabaseAdapter

        return DatabaseAdapter.quote_relation_name(f"{self.schema}.{self.table}")

    @classmethod
    def from_string(cls, table_name_full: str) -> "TableAddress":
        return TableAddress(*table_name_full.split("."))


@dataclasses.dataclass
class ClusterInformation:
    """
    Manage a database cluster's information.
    """

    cratedb: t.Any = dataclasses.field(default_factory=dict)
    cloud: t.Dict[str, t.Any] = dataclasses.field(default_factory=dict)

    def asdict(self):
        return dataclasses.asdict(self)


@dataclasses.dataclass
class InputOutputResource:
    """
    Manage information about an input or output resource.
    """

    url: str
    format: t.Optional[str] = None  # noqa: A003
    compression: t.Optional[str] = None


@define
class AddressPair:
    """
    Manage two URL instances, specifically a pair of source/target URLs,
    where target is mostly a CrateDB Server, while source is any.
    """

    source_url: URL
    target_url: URL

    _source_url_query_parameters: t.Dict[str, t.Any] = Factory(dict)
    _target_url_query_parameters: t.Dict[str, t.Any] = Factory(dict)

    __SERVER_SCHEMES__ = ["http", "https", "mongodb", "mongodb+srv"]

    def navigate(self, source_path: str, target_path: str) -> "AddressPair":
        source_url = deepcopy(self.source_url)
        target_url = deepcopy(self.target_url)

        # Q: What the hack?
        # A: Adjustments about missing trailing slashes, business as usual.
        #    It makes subsequent `.navigate()` operations work.
        # Remark: It is not applicable for filesystem paths including wildcards,
        #         like `./datasets/*.ndjson`. In this case, `.navigate()` should
        #         strip the `*.ndjson` part, and replace it by the designated label.
        if source_url.scheme in self.__SERVER_SCHEMES__ and source_url.path[-1] != "/":
            source_url.path += "/"
        if target_url.path[-1] != "/":
            target_url.path += "/"

        source_url.path = urljoin(source_url.path, source_path)
        target_url.path = urljoin(target_url.path, target_path)

        return AddressPair(source_url, target_url)
