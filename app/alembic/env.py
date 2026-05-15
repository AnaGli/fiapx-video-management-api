import os  # Adicionado para ler variáveis de ambiente
from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Setup de caminhos
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

# Import dos seus modelos
from app.database import Base
from app.models.client import Client
from app.models.vehicle import Vehicle
from app.models.service import Service
from app.models.part import Part
from app.models.stock_movement import StockMovement
from app.models.user import User
from app.models.service_order import ServiceOrder
from app.models.service_order_item import ServiceOrderItem

# Setup de caminhos
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

target_metadata = Base.metadata

# Configuração do Alembic
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def get_url():
    """Busca a URL da variável de ambiente ou do alembic.ini."""
    return os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url() # Usa a função que prioriza o ambiente
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # Criamos a configuração dinamicamente para injetar a URL do ambiente
    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = get_url() # Sobrescreve com a env var

    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()