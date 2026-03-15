"""
Base SQLModel Configuration

This module initializes SQLModel and provides base classes for all database models.
All models should inherit from SQLModel and be imported here for Alembic autogeneration.
"""

from sqlmodel import SQLModel

# Import all models here so Alembic can detect them for migrations
from src.models.user import User, UserPublic
from src.models.user_settings import UserSettings, UserSettingsUpdate, UserProfileUpdate, ChangePasswordRequest
from src.models.task import Task, TaskPublic, TaskCreate, TaskUpdate, TaskCompletionToggle
from src.models.tag import Tag, TagPublic, TagCreate, TagUpdate
from src.models.task_tag import TaskTag
from src.models.team import Team, TeamCreate, TeamUpdate, TeamPublic
from src.models.team_member import TeamMember, TeamMemberCreate, TeamMemberUpdate, TeamMemberPublic
from src.models.team_invitation import TeamInvitation, TeamInvitationCreate, TeamInvitationPublic
from src.models.comment import Comment, CommentCreate, CommentUpdate, CommentPublic
from src.models.task_assignment import TaskAssignment, TaskAssignmentCreate, TaskAssignmentPublic
from src.models.project import Project, ProjectCreate, ProjectUpdate, ProjectPublic
from src.models.milestone import Milestone, MilestoneCreate, MilestoneUpdate, MilestonePublic
from src.models.task_dependency import TaskDependency, TaskDependencyCreate, TaskDependencyPublic
from src.models.notification import Notification, NotificationCreate, NotificationPublic
from src.models.notification_preference import NotificationPreference, NotificationPreferenceCreate, NotificationPreferenceUpdate, NotificationPreferencePublic
from src.models.analytics_snapshot import AnalyticsSnapshot, AnalyticsSnapshotCreate, AnalyticsSnapshotPublic
from src.models.custom_report import CustomReport, CustomReportCreate, CustomReportPublic
from src.models.conversation import Conversation, ConversationPublic, ConversationCreate, ConversationList
from src.models.message import Message, MessagePublic, MessageCreate, MessageList

__all__ = [
    "SQLModel",
    "User",
    "UserPublic",
    "UserSettings",
    "UserSettingsUpdate",
    "UserProfileUpdate",
    "ChangePasswordRequest",
    "Task",
    "TaskPublic",
    "TaskCreate",
    "TaskUpdate",
    "TaskCompletionToggle",
    "Tag",
    "TagPublic",
    "TagCreate",
    "TagUpdate",
    "TaskTag",
    "Team",
    "TeamCreate",
    "TeamUpdate",
    "TeamPublic",
    "TeamMember",
    "TeamMemberCreate",
    "TeamMemberUpdate",
    "TeamMemberPublic",
    "TeamInvitation",
    "TeamInvitationCreate",
    "TeamInvitationPublic",
    "Comment",
    "CommentCreate",
    "CommentUpdate",
    "CommentPublic",
    "TaskAssignment",
    "TaskAssignmentCreate",
    "TaskAssignmentPublic",
    "Project",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectPublic",
    "Milestone",
    "MilestoneCreate",
    "MilestoneUpdate",
    "MilestonePublic",
    "TaskDependency",
    "TaskDependencyCreate",
    "TaskDependencyPublic",
    "Notification",
    "NotificationCreate",
    "NotificationPublic",
    "NotificationPreference",
    "NotificationPreferenceCreate",
    "NotificationPreferenceUpdate",
    "NotificationPreferencePublic",
    "AnalyticsSnapshot",
    "AnalyticsSnapshotCreate",
    "AnalyticsSnapshotPublic",
    "CustomReport",
    "CustomReportCreate",
    "CustomReportPublic",
    "Conversation",
    "ConversationPublic",
    "ConversationCreate",
    "ConversationList",
    "Message",
    "MessagePublic",
    "MessageCreate",
    "MessageList",
]
