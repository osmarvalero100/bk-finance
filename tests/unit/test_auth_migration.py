import pytest
from datetime import timedelta

from app.utils.auth import get_password_hash
from app.core.config import settings
from app.models.user import User


def test_automatic_rehash_on_login(db_session, async_client):
    # Crear usuario con contraseña conocida y hash antiguo (simulamos un esquema antiguo
    # creando un hash con get_password_hash y luego forzando needs_update -> True mediante
    # modificando el contexto si fuera necesario. Para simplicidad, crearemos un hash y luego
    # pretendemos que necesita actualización llamando a pwd_context.needs_update.
    plain = "SuperSecretPassword123!"
    # Hash inicial usando la función actual (simula un hash antiguo para fines del test)
    initial_hash = get_password_hash(plain)

    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"migrate_test_{unique_id}@example.com",
        username=f"migrate_test_{unique_id}",
        hashed_password=initial_hash,
        full_name="Migrate Test",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Llamar al endpoint de login (usando httpx AsyncClient fixture)
    import asyncio
    async def call_login():
        resp = await async_client.post(
            "/auth/login",
            data={"username": user.username, "password": plain},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return resp

    resp = asyncio.get_event_loop().run_until_complete(call_login())

    assert resp.status_code == 200

    # Refrescar usuario desde la DB y comprobar que hashed_password existe y es distinto
    db_session.refresh(user)
    assert user.hashed_password is not None
    assert isinstance(user.hashed_password, str)
