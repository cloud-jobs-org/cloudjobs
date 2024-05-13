import uuid
from datetime import datetime, timedelta

from pydantic import BaseModel, Field


class Notification(BaseModel):
    game_id: str
    title: str
    message: str
    category: str
    time_read: datetime | None
    is_read: bool
    time_created: datetime


class NotificationsModel(BaseModel):

    notifications: list[Notification]

    @property
    def unread_notification(self) -> list[Notification]:
        return [notice for notice in self.notifications
                if not notice.is_read] if isinstance(self.notifications, list) else []

    @property
    def all_notifications(self) -> list[Notification]:
        return self.notifications

    @property
    def day_old_notifications(self) -> list[Notification]:
        """
        Get notifications that are at least one day old.
        :return: List of day-old notifications
        """
        a_day_ago = datetime.now() - timedelta(hours=24)
        return [notice for notice in self.notifications if notice.time_created < a_day_ago]


class CreateNotification(BaseModel):
    game_id: str = Field(default_factory=lambda: uuid.uuid4())
    title: str
    message: str
    category: str
    time_read: datetime | None
    is_read: bool = Field(default=False)
    time_created: datetime = Field(default_factory=lambda: datetime.now())

