"""
Database Connection

This module provides the Database class for managing PostgreSQL connections
using asyncpg with async/await support.

Example:
    >>> from sillys.md.core import Database
    >>> db = Database()
    >>> await db.init_db("postgresql://user:pass@localhost/dbname")
    >>> result = await db.fetch("SELECT * FROM users")
    >>> await db.close_db()
"""

import asyncio
from typing import Any, Dict, List, Optional

try:
    import asyncpg
    from asyncpg import Pool, Connection
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False
    Pool = None
    Connection = None


class Database:
    """
    PostgreSQL database connection manager with async support.

    This class provides a high-level interface for database operations,
    connection pooling, and lifecycle management.

    Attributes:
        _pool: The asyncpg connection pool.
        _config: Database connection configuration.
        _initialized: Whether the database has been initialized.

    Example:
        >>> db = Database()
        >>> await db.init_db(database_url="postgresql://user:pass@localhost/db")
        >>>
        >>> # Fetch rows
        >>> users = await db.fetch("SELECT * FROM users WHERE active = $1", True)
        >>>
        >>> # Execute operations
        >>> await db.execute("INSERT INTO logs (message) VALUES ($1)", "User logged in")
        >>>
        >>> # Transaction support
        >>> async with db.transaction() as conn:
        ...     await conn.execute("INSERT INTO orders (user_id) VALUES ($1)", user_id)
        >>>
        >>> await db.close_db()
    """

    _instance: Optional["Database"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "Database":
        """Ensure singleton pattern for Database."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            cls._instance._pool = None
            cls._instance._config: Dict[str, Any] = {}
        return cls._instance

    def __init__(self) -> None:
        """Initialize the database instance."""
        if not hasattr(self, "_initialized"):
            self._initialized = False
            self._pool: Optional["Pool"] = None
            self._config: Dict[str, Any] = {}

    @property
    def is_initialized(self) -> bool:
        """Check if the database has been initialized."""
        return self._initialized

    @property
    def pool(self) -> Optional["Pool"]:
        """Get the connection pool."""
        return self._pool

    async def init_db(
        self,
        database_url: Optional[str] = None,
        *,
        host: Optional[str] = None,
        port: int = 5432,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        min_size: int = 10,
        max_size: int = 20,
        command_timeout: float = 60.0,
        max_queries: int = 50000,
        max_inactive_connection_lifetime: float = 300.0,
        setup: Optional[callable] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        """
        Initialize the database connection pool.

        Can be called with either a database URL or individual connection parameters.

        Args:
            database_url: PostgreSQL connection URL (e.g., "postgresql://user:pass@localhost/db").
            host: Database host name.
            port: Database port (default: 5432).
            user: Database user.
            password: Database password.
            database: Database name.
            min_size: Minimum pool size (default: 10).
            max_size: Maximum pool size (default: 20).
            command_timeout: Query command timeout in seconds (default: 60.0).
            max_queries: Maximum queries per connection before reconnect.
            max_inactive_connection_lifetime: Max inactive connection lifetime in seconds.
            setup: Optional setup function called on new connections.
            loop: Optional event loop instance.

        Raises:
            ImportError: If asyncpg is not installed.
            ValueError: If required parameters are missing.
        """
        if not HAS_ASYNCPG:
            raise ImportError(
                "asyncpg is required for database operations. Install with: pip install asyncpg"
            )

        if database_url:
            self._config = {"database_url": database_url}
            self._pool = await asyncpg.create_pool(
                database_url,
                min_size=min_size,
                max_size=max_size,
                command_timeout=command_timeout,
                max_queries=max_queries,
                max_inactive_connection_lifetime=max_inactive_connection_lifetime,
                setup=setup,
                loop=loop,
            )
        else:
            if not all([host, user, password, database]):
                raise ValueError(
                    "Either database_url or host, user, password, and database must be provided"
                )
            self._config = {
                "host": host,
                "port": port,
                "user": user,
                "password": password,
                "database": database,
            }
            self._pool = await asyncpg.create_pool(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                min_size=min_size,
                max_size=max_size,
                command_timeout=command_timeout,
                max_queries=max_queries,
                max_inactive_connection_lifetime=max_inactive_connection_lifetime,
                setup=setup,
                loop=loop,
            )

        self._initialized = True

    async def close_db(self) -> None:
        """
        Close the database connection pool.

        This should be called during application shutdown.
        """
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            self._initialized = False

    async def fetch(self, query: str, *args: Any) -> List[asyncpg.Record]:
        """
        Execute a SELECT query and return all rows.

        Args:
            query: SQL query string.
            *args: Query parameters.

        Returns:
            List of asyncpg.Record objects.

        Raises:
            RuntimeError: If database is not initialized.
        """
        if not self._pool:
            raise RuntimeError("Database not initialized. Call init_db() first.")

        async with self._pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> Optional[asyncpg.Record]:
        """
        Execute a SELECT query and return a single row.

        Args:
            query: SQL query string.
            *args: Query parameters.

        Returns:
            A single asyncpg.Record or None if no rows found.

        Raises:
            RuntimeError: If database is not initialized.
        """
        if not self._pool:
            raise RuntimeError("Database not initialized. Call init_db() first.")

        async with self._pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

    async def execute(self, query: str, *args: Any) -> str:
        """
        Execute a query that doesn't return rows (INSERT, UPDATE, DELETE, etc.).

        Args:
            query: SQL query string.
            *args: Query parameters.

        Returns:
            Status string from the database.

        Raises:
            RuntimeError: If database is not initialized.
        """
        if not self._pool:
            raise RuntimeError("Database not initialized. Call init_db() first.")

        async with self._pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def executemany(self, command: str, *args_list: Any) -> None:
        """
        Execute a command multiple times with different parameters.

        Args:
            command: SQL command string.
            *args_list: Sequence of parameter tuples.

        Raises:
            RuntimeError: If database is not initialized.
        """
        if not self._pool:
            raise RuntimeError("Database not initialized. Call init_db() first.")

        async with self._pool.acquire() as connection:
            await connection.executemany(command, args_list)

    async def copy_to_table(
        self,
        table_name: str,
        *,
        columns: Optional[List[str]] = None,
        format: str = "csv",
        oids: bool = False,
        delimiter: str = ",",
        null: str = "",
        header: bool = True,
    ) -> bytes:
        """
        Copy data from a file-like object to a table.

        Args:
            table_name: Name of the table to copy to.
            columns: List of column names.
            format: Copy format ("csv" or "text").
            oids: Include OIDs.
            delimiter: Field delimiter.
            null: NULL representation.
            header: Include header row.

        Returns:
            Copy result as bytes.

        Raises:
            RuntimeError: If database is not initialized.
        """
        if not self._pool:
            raise RuntimeError("Database not initialized. Call init_db() first.")

        async with self._pool.acquire() as connection:
            return await connection.copy_to_table(
                table_name,
                columns=columns,
                format=format,
                oids=oids,
                delimiter=delimiter,
                null=null,
                header=header,
            )

    def transaction(self) -> "Transaction":
        """
        Get a transaction context manager.

        Returns:
            Transaction context manager.

        Example:
            >>> async with db.transaction() as conn:
            ...     await conn.execute("INSERT INTO users (name) VALUES ($1)", "John")
            ...     await conn.execute("INSERT INTO orders (user_id) VALUES ($1)", user_id)
        """
        if not self._pool:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return Transaction(self._pool)


class Transaction:
    """
    Async context manager for database transactions.

    Example:
        >>> async with db.transaction() as conn:
        ...     await conn.execute("INSERT INTO users (name) VALUES ($1)", "John")
    """

    def __init__(self, pool: "Pool") -> None:
        """
        Initialize the transaction.

        Args:
            pool: The asyncpg connection pool.
        """
        self._pool = pool
        self._connection: Optional["Connection"] = None

    async def __aenter__(self) -> "Connection":
        """Enter the transaction context."""
        self._connection = await self._pool.acquire()
        await self._connection.execute("BEGIN")
        return self._connection

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the transaction context."""
        if self._connection is None:
            return

        if exc_type is not None:
            await self._connection.execute("ROLLBACK")
        else:
            await self._connection.execute("COMMIT")

        await self._pool.release(self._connection)
        self._connection = None


def get_db() -> Database:
    """
    Get the singleton Database instance.

    Returns:
        The Database singleton instance.
    """
    return Database()


def get_db_pool() -> Optional["Pool"]:
    """
    Get the database connection pool.

    Returns:
        The asyncpg Pool instance, or None if not initialized.
    """
    return Database().pool


async def init_db(*args: Any, **kwargs: Any) -> None:
    """
    Initialize the database connection pool.

    See Database.init_db() for parameters.
    """
    await Database().init_db(*args, **kwargs)


async def close_db() -> None:
    """Close the database connection pool."""
    await Database().close_db()
