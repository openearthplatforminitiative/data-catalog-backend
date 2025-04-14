"""empty message

Revision ID: 1a2507fbaa74
Revises: 6e12e67cc51c
Create Date: 2025-04-14 09:04:48.607851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a2507fbaa74'
down_revision: Union[str, None] = '6e12e67cc51c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('resource_category', 'is_main_category',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.create_index('only_one_main_category_per_resource', 'resource_category', ['resource_id'], unique=True, postgresql_where=sa.text('is_main_category = true'))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('only_one_main_category_per_resource', table_name='resource_category', postgresql_where=sa.text('is_main_category = true'))
    op.alter_column('resource_category', 'is_main_category',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###
