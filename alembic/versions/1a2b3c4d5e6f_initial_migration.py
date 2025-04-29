"""Initial database schema

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2023-04-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a2b3c4d5e6f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create search_analyses table
    op.create_table(
        'search_analyses',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('search_term', sa.String(255), nullable=False),
        sa.Column('main_keyword', sa.String(255), nullable=False),
        sa.Column('secondary_keywords', sa.JSON, nullable=False),
        sa.Column('intent_type', sa.String(50), nullable=False),
        sa.Column('has_market_gap', sa.Boolean(), server_default='FALSE'),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('search_term')
    )
    
    # Create serp_features table
    op.create_table(
        'serp_features',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('analysis_id', sa.String(36), sa.ForeignKey('search_analyses.id')),
        sa.Column('feature_type', sa.String(50), nullable=False),
        sa.Column('feature_position', sa.Integer),
        sa.Column('feature_data', sa.JSON),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Create recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('analysis_id', sa.String(36), sa.ForeignKey('search_analyses.id')),
        sa.Column('tactic_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Create indexes
    op.create_index('idx_search_term', 'search_analyses', ['search_term'])
    op.create_index('idx_analysis_features', 'serp_features', ['analysis_id'])
    op.create_index('idx_analysis_recommendations', 'recommendations', ['analysis_id'])


def downgrade() -> None:
    # Drop tables in reverse order to handle dependencies
    op.drop_table('recommendations')
    op.drop_table('serp_features')
    op.drop_table('search_analyses') 