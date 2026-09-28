"""Cria um usuário administrador ou promove um usuário existente a admin.

Uso:
    python -m scripts.create_admin --email admin@layer.com --name "Admin"
"""

import argparse
import getpass

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import User, UserRole
from app.repositories.user import UserRepository


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria ou promove um administrador.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()

    with SessionLocal() as db:
        users = UserRepository(db)
        user = users.get_by_email(args.email)

        if user is not None:
            user.role = UserRole.ADMIN
            db.commit()
            print(f"Usuário {user.email} promovido a administrador.")
            return

        password = getpass.getpass("Senha do novo admin: ")
        if len(password) < 8:
            raise SystemExit("A senha precisa ter pelo menos 8 caracteres.")

        users.create(
            User(
                email=args.email.lower(),
                name=args.name,
                hashed_password=hash_password(password),
                role=UserRole.ADMIN,
            )
        )
        print(f"Administrador {args.email.lower()} criado.")


if __name__ == "__main__":
    main()
