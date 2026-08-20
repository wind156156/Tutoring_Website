"""Add tutoring website tables
Revision ID: 001
Revises:
Create Date: 2026-08-13
"""
from alembic import op
import sqlalchemy as sa


revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('nickname', sa.String(length=50), nullable=False),
        sa.Column('avatar', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('phone', name='uq_users_phone'),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )

    # parents
    op.create_table('parents',
        sa.Column('user_id', sa.Integer(), primary_key=True),
        sa.Column('real_name', sa.String(length=50), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # teachers
    op.create_table('teachers',
        sa.Column('user_id', sa.Integer(), primary_key=True),
        sa.Column('real_name', sa.String(length=50), nullable=False),
        sa.Column('id_card', sa.String(length=20), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('birth_year', sa.Integer(), nullable=True),
        sa.Column('education', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('subject_tags', sa.Text(), nullable=False),
        sa.Column('experience_years', sa.Integer(), nullable=False),
        sa.Column('hourly_rate', sa.Numeric(8, 2), nullable=False),
        sa.Column('city', sa.String(length=50), nullable=False),
        sa.Column('district', sa.String(length=50), nullable=False),
        sa.Column('qualification_url', sa.String(length=500), nullable=False),
        sa.Column('bio', sa.Text(), nullable=False),
        sa.Column('rating_avg', sa.Numeric(3, 2), nullable=False),
        sa.Column('rating_count', sa.Integer(), nullable=False),
        sa.Column('completed_orders', sa.Integer(), nullable=False),
        sa.Column('is_verified', sa.SmallInteger(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('id_card', name='uq_teachers_id_card'),
    )

    # students
    op.create_table('students',
        sa.Column('user_id', sa.Integer(), primary_key=True),
        sa.Column('real_name', sa.String(length=50), nullable=False),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('birth_year', sa.Integer(), nullable=True),
        sa.Column('grade', sa.String(length=20), nullable=False),
        sa.Column('school', sa.String(length=100), nullable=False),
        sa.Column('subjects', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['parents.user_id']),
    )

    # bindings
    op.create_table('teacher_student_bindings',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('reply_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('expire_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.user_id']),
        sa.ForeignKeyConstraint(['student_id'], ['students.user_id']),
        sa.ForeignKeyConstraint(['parent_id'], ['parents.user_id']),
        sa.UniqueConstraint('teacher_id', 'student_id', name='uq_teacher_student'),
        sa.Index('idx_teacher_status', 'teacher_id', 'status'),
        sa.Index('idx_parent_bindings', 'parent_id', 'status'),
    )

    # assignments
    op.create_table('assignments',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content_images', sa.Text(), nullable=True),
        sa.Column('due_at', sa.DateTime(), nullable=False),
        sa.Column('max_score', sa.Numeric(6, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.user_id']),
        sa.Index('idx_teacher_created', 'teacher_id', 'created_at'),
        sa.Index('idx_due', 'due_at'),
    )

    # assignment_students
    op.create_table('assignment_students',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('assignment_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Numeric(6, 2), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('graded_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['assignment_id'], ['assignments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.user_id']),
        sa.Index('idx_assignment_status', 'assignment_id', 'status'),
    )

    # submission_files
    op.create_table('submission_files',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('assignment_student_id', sa.Integer(), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=200), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['assignment_student_id'], ['assignment_students.id'], ondelete='CASCADE'),
        sa.Index('idx_as', 'assignment_student_id'),
    )

    # favorites
    op.create_table('favorites',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.user_id'], ondelete='CASCADE'),
        sa.Index('idx_user', 'user_id'),
        sa.UniqueConstraint('user_id', 'teacher_id', name='uq_user_teacher'),
    )

    # announcements
    op.create_table('announcements',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('publish_from', sa.DateTime(), nullable=False),
        sa.Column('publish_to', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.SmallInteger(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.Index('idx_active_publish', 'is_active', 'publish_from', 'publish_to'),
    )

    # audit_logs
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('ip', sa.String(length=45), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Index('idx_user_action', 'user_id', 'action'),
        sa.Index('idx_created', 'created_at'),
    )

    # im_conversations
    op.create_table('im_conversations',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('conversation_key', sa.String(length=64), nullable=False),
        sa.Column('participant_1_id', sa.Integer(), nullable=False),
        sa.Column('participant_2_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('conversation_key', name='uq_im_conv_key'),
        sa.Index('idx_p1_p2', 'participant_1_id', 'participant_2_id'),
    )

    # im_messages
    op.create_table('im_messages',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('receiver_id', sa.Integer(), nullable=False),
        sa.Column('msg_type', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_read', sa.SmallInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['im_conversations.id'], ondelete='CASCADE'),
        sa.Index('idx_conv_time', 'conversation_id', 'created_at'),
        sa.Index('idx_sender', 'sender_id', 'created_at'),
        sa.Index('idx_receiver_unread', 'receiver_id', 'is_read', 'created_at'),
    )


def downgrade() -> None:
    op.drop_table('im_messages')
    op.drop_table('im_conversations')
    op.drop_table('audit_logs')
    op.drop_table('announcements')
    op.drop_table('favorites')
    op.drop_table('submission_files')
    op.drop_table('assignment_students')
    op.drop_table('assignments')
    op.drop_table('teacher_student_bindings')
    op.drop_table('students')
    op.drop_table('teachers')
    op.drop_table('parents')
    op.drop_table('users')
