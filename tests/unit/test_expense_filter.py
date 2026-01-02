import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from datetime import UTC
from sqlalchemy.orm import Session
from app.models.expense import Expense
from app.models.category import Category
from app.models.tag import Tag

class TestExpenseFilter:
    """Tests para el endpoint de filtrado de gastos"""

    @pytest.mark.asyncio
    async def test_filter_by_date_range(self, async_client: AsyncClient, auth_headers, db_session: Session, test_user, test_category):
        """Test filtrar por rango de fechas"""
        # Crear gastos en diferentes fechas
        # Usar fechas fijas sin segundos para evitar problemas de parsing
        base_date = datetime.now(UTC).replace(second=0, microsecond=0)
        e1 = Expense(user_id=test_user.id, category_id=test_category.id, amount=10.0, description="D1", date=base_date - timedelta(days=5))
        e2 = Expense(user_id=test_user.id, category_id=test_category.id, amount=20.0, description="D2", date=base_date - timedelta(days=2))
        e3 = Expense(user_id=test_user.id, category_id=test_category.id, amount=30.0, description="D3", date=base_date)
        db_session.add_all([e1, e2, e3])
        db_session.commit()

        start = (base_date - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
        end = (base_date - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
        
        response = await async_client.get(f"/expenses/filter?start_date={start}&end_date={end}", headers=auth_headers)
        if response.status_code == 422:
            print(f"\nError 422 details (Date Range): {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["description"] == "D2"

    @pytest.mark.asyncio
    async def test_filter_by_amount_range(self, async_client: AsyncClient, auth_headers, db_session: Session, test_user, test_category):
        """Test filtrar por rango de montos"""
        e1 = Expense(user_id=test_user.id, category_id=test_category.id, amount=10.0, description="A10", date=datetime.now(UTC))
        e2 = Expense(user_id=test_user.id, category_id=test_category.id, amount=50.0, description="A50", date=datetime.now(UTC))
        e3 = Expense(user_id=test_user.id, category_id=test_category.id, amount=100.0, description="A100", date=datetime.now(UTC))
        db_session.add_all([e1, e2, e3])
        db_session.commit()

        response = await async_client.get("/expenses/filter?min_amount=40&max_amount=60", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["amount"] == 50.0

    @pytest.mark.asyncio
    async def test_filter_by_description(self, async_client: AsyncClient, auth_headers, db_session: Session, test_user, test_category):
        """Test filtrar por descripción (búsqueda parcial)"""
        e1 = Expense(user_id=test_user.id, category_id=test_category.id, amount=10.0, description="Supermarket", date=datetime.now(UTC))
        e2 = Expense(user_id=test_user.id, category_id=test_category.id, amount=20.0, description="Dinner at Restaurant", date=datetime.now(UTC))
        db_session.add_all([e1, e2])
        db_session.commit()

        response = await async_client.get("/expenses/filter?description=rest", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Restaurant" in data[0]["description"]

    @pytest.mark.asyncio
    async def test_filter_by_tags(self, async_client: AsyncClient, auth_headers, db_session: Session, test_user, test_category):
        """Test filtrar por etiquetas"""
        tag1 = Tag(user_id=test_user.id, name="Tag1", color="#FF0000")
        tag2 = Tag(user_id=test_user.id, name="Tag2", color="#00FF00")
        db_session.add_all([tag1, tag2])
        db_session.commit()

        e1 = Expense(user_id=test_user.id, category_id=test_category.id, amount=10.0, description="E1", date=datetime.now(UTC))
        e1.tags.append(tag1)
        e2 = Expense(user_id=test_user.id, category_id=test_category.id, amount=20.0, description="E2", date=datetime.now(UTC))
        e2.tags.append(tag2)
        
        db_session.add_all([e1, e2])
        db_session.commit()

        response = await async_client.get(f"/expenses/filter?tag_ids={tag1.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["description"] == "E1"
