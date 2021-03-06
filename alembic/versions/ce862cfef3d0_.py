"""empty message

Revision ID: ce862cfef3d0
Revises: 910108f8e7f7
Create Date: 2019-06-30 23:28:24.653651

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce862cfef3d0'
down_revision = '910108f8e7f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('day_list_id_fkey', 'day', type_='foreignkey')
    op.create_foreign_key(None, 'day', 'list', ['list_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('foods_list_id_fkey', 'foods', type_='foreignkey')
    op.create_foreign_key(None, 'foods', 'list', ['list_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('ingredients_food_id_fkey', 'ingredients', type_='foreignkey')
    op.create_foreign_key(None, 'ingredients', 'foods', ['food_id'], ['id'], ondelete='CASCADE')
    op.alter_column('listsettings', 'list_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('listsettings', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_constraint('listsettings_user_id_fkey', 'listsettings', type_='foreignkey')
    op.drop_constraint('listsettings_list_id_fkey', 'listsettings', type_='foreignkey')
    op.create_foreign_key(None, 'listsettings', 'list', ['list_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'listsettings', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('meals_list_id_fkey', 'meals', type_='foreignkey')
    op.create_foreign_key(None, 'meals', 'list', ['list_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'meals', type_='foreignkey')
    op.create_foreign_key('meals_list_id_fkey', 'meals', 'list', ['list_id'], ['id'])
    op.drop_constraint(None, 'listsettings', type_='foreignkey')
    op.drop_constraint(None, 'listsettings', type_='foreignkey')
    op.create_foreign_key('listsettings_list_id_fkey', 'listsettings', 'list', ['list_id'], ['id'])
    op.create_foreign_key('listsettings_user_id_fkey', 'listsettings', 'user', ['user_id'], ['id'])
    op.alter_column('listsettings', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('listsettings', 'list_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_constraint(None, 'ingredients', type_='foreignkey')
    op.create_foreign_key('ingredients_food_id_fkey', 'ingredients', 'foods', ['food_id'], ['id'])
    op.drop_constraint(None, 'foods', type_='foreignkey')
    op.create_foreign_key('foods_list_id_fkey', 'foods', 'list', ['list_id'], ['id'])
    op.drop_constraint(None, 'day', type_='foreignkey')
    op.create_foreign_key('day_list_id_fkey', 'day', 'list', ['list_id'], ['id'])
    # ### end Alembic commands ###
