import socket
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings
from backend.app.core.logging import logger

Base = declarative_base()

def is_postgres_reachable(host: str = "localhost", port: int = 5432, timeout: float = 0.4) -> bool:
    """Fast non-blocking check if PostgreSQL port is actively listening."""
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def get_engine():
    pg_url = settings.DATABASE_URL
    # Check if Postgres host/port is reachable
    if pg_url and pg_url.startswith("postgresql") and is_postgres_reachable(settings.POSTGRES_HOST, int(settings.POSTGRES_PORT)):
        try:
            pg_engine = create_engine(
                pg_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                connect_args={"connect_timeout": 2}
            )
            with pg_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Connected successfully to PostgreSQL database: {settings.POSTGRES_DB}")
            return pg_engine
        except Exception as e:
            logger.warning(
                f"PostgreSQL connection failed ({e}). Falling back to SQLite database."
            )
            
    # SQLite fallback
    sqlite_engine = create_engine(
        settings.SQLITE_URL,
        connect_args={"check_same_thread": False}
    )
    try:
        with sqlite_engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL;"))
            conn.execute(text("PRAGMA foreign_keys=ON;"))
    except Exception as e:
        logger.debug(f"SQLite PRAGMA setup notice: {e}")
    logger.info(f"Using SQLite database engine at {settings.SQLITE_URL}")
    return sqlite_engine

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
