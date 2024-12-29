from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, BIGINT, BOOLEAN, VARCHAR, TIMESTAMP
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.types import String
from bot.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[BIGINT] = mapped_column(BIGINT, primary_key=True)
    first_name: Mapped[VARCHAR] = mapped_column(VARCHAR, nullable=False)
    last_name: Mapped[VARCHAR] = mapped_column(VARCHAR, nullable=False)
    username: Mapped[VARCHAR] = mapped_column(VARCHAR, nullable=False)
    language_code: Mapped[VARCHAR] = mapped_column(VARCHAR, nullable=False)
    allows_write_to_pm: Mapped[BOOLEAN] = mapped_column(BOOLEAN, nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=False)
    updated_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=False)
