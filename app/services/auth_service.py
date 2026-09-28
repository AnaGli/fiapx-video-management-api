from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def register(self, data: UserCreate) -> User:
        existing_username = self.user_repository.find_by_username(
            data.username
        )

        if existing_username:
            raise ValueError("Username already exists")

        existing_email = self.user_repository.find_by_email(
            data.email
        )

        if existing_email:
            raise ValueError("Email already exists")

        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
        )

        return self.user_repository.create(user)

    def login(
        self,
        username: str,
        password: str,
    ) -> str:
        user = self.user_repository.find_by_username(username)

        if not user:
            raise ValueError("Invalid username or password")

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError("Invalid username or password")

        return create_access_token(str(user.id))