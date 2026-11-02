"""fix

Revision ID: 1c8d6c5c6a99
Revises: e5f57316134f
Create Date: 2026-11-03 01:41:39.308581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c8d6c5c6a99'
down_revision: Union[str, Sequence[str], None] = 'e5f57316134f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Явно указываем существующий тип колонки, отключая autoincrement
    op.alter_column('user_roles', 'user_id', autoincrement=False)
    op.alter_column('user_roles', 'role_id', autoincrement=False)

def downgrade() -> None:
    # Возвращаем обратно в случае отката (обычно Postgres не требует тут ничего менять)
    op.alter_column('user_roles', 'user_id', autoincrement=True)
    op.alter_column('user_roles', 'role_id', autoincrement=True)
