from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    def register(self, data: UserCreate) -> User:
        if self.users.get_by_email(data.email):
            raise ConflictError("Email already registered")

        user = User(
            email=data.email,
            name=data.name,
            hashed_password=hash_password(data.password),
        )
        return self.users.create(user)

    def authenticate(self, email: str, password: str) -> str:
        user = self.users.get_by_email(email)

        credentials_valid = user is not None and verify_password(
            password, user.hashed_password
        )
        if not credentials_valid or not user.is_active:
            raise UnauthorizedError("Incorrect email or password")

        return create_access_token(str(user.id))
