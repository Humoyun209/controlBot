"""Initial

Revision ID: 6cb173423b59
Revises: 
Create Date: 2023-12-28 23:16:11.947139

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cb173423b59'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('technical_map', sa.String(), nullable=True),
    sa.Column('live', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('username', sa.String(length=32), nullable=False),
    sa.Column('phone', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('updated', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('status', sa.Enum('ANONYMOUS', 'USER', 'ADMIN', 'SUPER', name='userstatus'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('worker',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('begin_shift',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('grams_of_tobacco', sa.Integer(), nullable=False),
    sa.Column('summa', sa.Numeric(), nullable=False),
    sa.Column('photo1', sa.String(), nullable=False),
    sa.Column('photo2', sa.String(), nullable=False),
    sa.Column('photo3', sa.String(), nullable=False),
    sa.Column('photo4', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('worker_id', sa.Integer(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['worker_id'], ['worker.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('company_worker',
    sa.Column('worker_id', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['worker_id'], ['worker.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('worker_id', 'company_id')
    )
    op.create_table('end_shift',
    sa.Column('quantity_of_sold', sa.Integer(), nullable=False),
    sa.Column('promo_quantity', sa.Integer(), nullable=False),
    sa.Column('card', sa.Integer(), nullable=False),
    sa.Column('cash', sa.Integer(), nullable=False),
    sa.Column('in_club', sa.Integer(), nullable=False),
    sa.Column('in_club_card', sa.Integer(), nullable=False),
    sa.Column('in_club_cash', sa.Integer(), nullable=False),
    sa.Column('tips', sa.Numeric(), nullable=False),
    sa.Column('begin_shift_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('grams_of_tobacco', sa.Integer(), nullable=False),
    sa.Column('summa', sa.Numeric(), nullable=False),
    sa.Column('photo1', sa.String(), nullable=False),
    sa.Column('photo2', sa.String(), nullable=False),
    sa.Column('photo3', sa.String(), nullable=False),
    sa.Column('photo4', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.Column('worker_id', sa.Integer(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['begin_shift_id'], ['begin_shift.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['worker_id'], ['worker.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('end_shift')
    op.drop_table('company_worker')
    op.drop_table('begin_shift')
    op.drop_table('worker')
    op.drop_table('users')
    op.drop_table('company')
    # ### end Alembic commands ###
