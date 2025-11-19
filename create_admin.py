#!/usr/bin/env python
"""
Script para criar um usuário administrador inicial
"""
import asyncio
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession


async def create_admin_user():
    """Criar usuário administrador inicial"""

    async for db in get_db():
        try:
            # Verificar se já existe um admin
            from sqlalchemy import select
            stmt = select(User).where(User.username == "admin")
            result = await db.execute(stmt)
            existing_admin = result.scalar_one_or_none()

            if existing_admin:
                print("⚠️  Usuário 'admin' já existe!")
                print(f"   Email: {existing_admin.email}")
                print(f"   Username: {existing_admin.username}")
                return

            # Criar admin
            admin = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                full_name="Administrador",
                is_active=True,
                is_superuser=True
            )

            db.add(admin)
            await db.commit()
            await db.refresh(admin)

            print("✅ Usuário administrador criado com sucesso!")
            print("")
            print("   Credenciais:")
            print("   ============")
            print(f"   Email: {admin.email}")
            print(f"   Username: {admin.username}")
            print(f"   Password: admin123")
            print("")
            print("   ⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
            print("")
            print("   Para fazer login:")
            print('   curl -X POST "http://localhost:8000/api/v1/auth/login" \\')
            print('     -H "Content-Type: application/json" \\')
            print("     -d '{\"username\": \"admin\", \"password\": \"admin123\"}'")

        except Exception as e:
            print(f"❌ Erro ao criar administrador: {e}")
            await db.rollback()
        finally:
            await db.close()
            break


if __name__ == "__main__":
    print("")
    print("========================================")
    print("  Criando Usuário Administrador")
    print("========================================")
    print("")

    asyncio.run(create_admin_user())
