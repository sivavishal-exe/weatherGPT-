"""Initial WeatherGPT database schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-10 22:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )

    # Locations table
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column('name', sa.String(250), nullable=False, index=True),
        sa.Column('latitude', sa.Float(), nullable=False, index=True),
        sa.Column('longitude', sa.Float(), nullable=False, index=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('timezone', sa.String(100), server_default='UTC', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )

    # Weather observations
    op.create_table(
        'weather_observations',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('location_id', sa.Integer(), sa.ForeignKey('locations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('apparent_temperature', sa.Float(), nullable=False),
        sa.Column('humidity', sa.Float(), nullable=False),
        sa.Column('surface_pressure', sa.Float(), nullable=False),
        sa.Column('wind_speed', sa.Float(), nullable=False),
        sa.Column('wind_direction', sa.Float(), nullable=False),
        sa.Column('weather_code', sa.Integer(), nullable=False),
        sa.Column('condition_text', sa.String(250), nullable=False),
        sa.Column('data_source', sa.String(100), server_default='Open-Meteo', nullable=False),
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

    # Forecasts
    op.create_table(
        'forecasts',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('location_id', sa.Integer(), sa.ForeignKey('locations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('forecast_date', sa.String(20), nullable=False, index=True),
        sa.Column('temp_max', sa.Float(), nullable=False),
        sa.Column('temp_min', sa.Float(), nullable=False),
        sa.Column('precipitation_sum', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('precipitation_probability', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('weather_code', sa.Integer(), nullable=False),
        sa.Column('condition_text', sa.String(250), nullable=False),
        sa.Column('data_source', sa.String(100), server_default='Open-Meteo', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

    # Severe alerts
    op.create_table(
        'severe_alerts',
        sa.Column('id', sa.String(250), primary_key=True, index=True),
        sa.Column('event', sa.String(250), nullable=False),
        sa.Column('severity', sa.String(50), nullable=False, index=True),
        sa.Column('headline', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('instruction', sa.Text(), nullable=True),
        sa.Column('source', sa.String(250), nullable=False),
        sa.Column('issued_at', sa.String(100), nullable=False),
        sa.Column('expires_at', sa.String(100), nullable=True),
        sa.Column('is_official_warning', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('latitude_min', sa.Float(), server_default='-90.0', nullable=False),
        sa.Column('latitude_max', sa.Float(), server_default='90.0', nullable=False),
        sa.Column('longitude_min', sa.Float(), server_default='-180.0', nullable=False),
        sa.Column('longitude_max', sa.Float(), server_default='180.0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

    # Saved locations
    op.create_table(
        'saved_locations',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('location_id', sa.Integer(), sa.ForeignKey('locations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('custom_alias', sa.String(250), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

    # Chat sessions
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('title', sa.String(250), server_default='Weather Query', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )

    # Chat messages
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('sender', sa.String(50), nullable=False),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=False),
        sa.Column('intent', sa.String(100), server_default='current', nullable=False),
        sa.Column('grounded_facts_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

    # Climate history
    op.create_table(
        'climate_history',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column('location_name', sa.String(250), nullable=False, index=True),
        sa.Column('month', sa.Integer(), nullable=False, index=True),
        sa.Column('baseline_avg_temp', sa.Float(), nullable=False),
        sa.Column('baseline_precip_mm', sa.Float(), nullable=False),
        sa.Column('baseline_period', sa.String(100), server_default='1991-2020 WMO Baseline', nullable=False),
        sa.Column('anomaly_temp', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

    # Advisories
    op.create_table(
        'advisories',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('observation_id', sa.String(36), sa.ForeignKey('weather_observations.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('advisory_type', sa.String(100), nullable=False, index=True),
        sa.Column('advisory_text', sa.Text(), nullable=False),
        sa.Column('risk_level', sa.String(50), server_default='LOW', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('advisories')
    op.drop_table('climate_history')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('saved_locations')
    op.drop_table('severe_alerts')
    op.drop_table('forecasts')
    op.drop_table('weather_observations')
    op.drop_table('locations')
    op.drop_table('users')
