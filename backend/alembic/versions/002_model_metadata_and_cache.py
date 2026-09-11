"""Model metadata and weather cache schema updates

Revision ID: 002_model_metadata_and_cache
Revises: 001_initial_schema
Create Date: 2026-09-11 14:27:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_model_metadata_and_cache'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Model Metadata table
    op.create_table(
        'model_metadata',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('model_name', sa.String(250), nullable=False, index=True),
        sa.Column('model_type', sa.String(100), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('adapter_path', sa.String(500), nullable=True),
        sa.Column('hyperparameters_json', sa.Text(), nullable=True),
        sa.Column('performance_metrics_json', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

    # Weather Cache table
    op.create_table(
        'weather_cache',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column('cache_key', sa.String(250), unique=True, nullable=False, index=True),
        sa.Column('payload_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.Float(), nullable=False),
        sa.Column('expires_at', sa.Float(), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('weather_cache')
    op.drop_table('model_metadata')
