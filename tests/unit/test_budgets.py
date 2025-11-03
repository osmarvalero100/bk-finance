import pytest
from httpx import AsyncClient
from datetime import date, datetime
from datetime import UTC
from sqlalchemy.orm import Session

class TestBudgetEndpoints:
    """Tests para endpoints de presupuestos"""

    @pytest.mark.asyncio
    async def test_create_budget_success(self, async_client: AsyncClient, auth_headers, db_session: Session, test_category):
        """Test crear presupuesto exitoso"""
        budget_data = {
            "name": "Monthly Budget",
            "description": "Budget for November 2024",
            "start_date": date.today().isoformat(),
            "end_date": date.today().replace(day=28).isoformat(),
            "currency": "COP",
            "is_active": True,
            "budget_items": [
                {
                    "category_id": test_category.id,
                    "budgeted_amount": 500.00,
                    "notes": "Food expenses"
                }
            ]
        }

        response = await async_client.post(
            "/budgets/",
            json=budget_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Monthly Budget"
        assert data["description"] == "Budget for November 2024"
        assert data["currency"] == "COP"
        assert data["total_budgeted"] == "500.00"
        assert len(data["budget_items"]) == 1
        assert data["budget_items"][0]["budgeted_amount"] == "500.00"
        assert "id" in data
        assert "user_id" in data

    @pytest.mark.asyncio
    async def test_create_budget_invalid_dates(self, async_client: AsyncClient, auth_headers):
        """Test crear presupuesto con fechas inválidas"""
        budget_data = {
            "name": "Invalid Budget",
            "start_date": date.today().replace(day=28).isoformat(),  # Fecha de fin antes de inicio
            "end_date": date.today().isoformat(),
            "currency": "COP",
            "budget_items": []
        }

        response = await async_client.post(
            "/budgets/",
            json=budget_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.json()
        assert "La fecha de inicio debe ser anterior a la fecha de fin" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_budgets_list(self, async_client: AsyncClient, auth_headers, test_budget):
        """Test obtener lista de presupuestos"""
        response = await async_client.get("/budgets/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Verificar que el presupuesto de prueba está en la lista
        budget_found = False
        for budget in data:
            if budget["id"] == test_budget.id:
                budget_found = True
                assert budget["name"] == test_budget.name
                assert budget["total_budgeted"] == str(test_budget.total_budgeted)
                break

        assert budget_found, "Test budget not found in response"

    @pytest.mark.asyncio
    async def test_get_budget_by_id(self, async_client: AsyncClient, auth_headers, test_budget):
        """Test obtener presupuesto por ID"""
        response = await async_client.get(
            f"/budgets/{test_budget.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_budget.id
        assert data["name"] == test_budget.name
        assert data["total_budgeted"] == str(test_budget.total_budgeted)

    @pytest.mark.asyncio
    async def test_get_budget_not_found(self, async_client: AsyncClient, auth_headers):
        """Test obtener presupuesto inexistente"""
        response = await async_client.get("/budgets/99999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "Presupuesto no encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_update_budget_success(self, async_client: AsyncClient, auth_headers, test_budget):
        """Test actualizar presupuesto exitoso"""
        update_data = {
            "name": "Updated Budget Name",
            "description": "Updated description"
        }

        response = await async_client.put(
            f"/budgets/{test_budget.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_budget.id
        assert data["name"] == "Updated Budget Name"
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_delete_budget_success(self, async_client: AsyncClient, auth_headers, test_budget):
        """Test eliminar presupuesto exitoso"""
        response = await async_client.delete(
            f"/budgets/{test_budget.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verificar que el presupuesto fue eliminado
        get_response = await async_client.get(
            f"/budgets/{test_budget.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_budget_item_success(self, async_client: AsyncClient, auth_headers, test_budget, test_category):
        """Test crear ítem de presupuesto exitoso"""
        item_data = {
            "category_id": test_category.id,
            "budgeted_amount": 300.00,
            "notes": "Additional budget item"
        }

        response = await async_client.post(
            f"/budgets/{test_budget.id}/items/",
            json=item_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["budget_id"] == test_budget.id
        assert data["category_id"] == test_category.id
        assert data["budgeted_amount"] == "300.00"
        assert data["notes"] == "Additional budget item"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_budget_item_duplicate_category(self, async_client: AsyncClient, auth_headers, test_budget, test_budget_item):
        """Test crear ítem con categoría duplicada"""
        item_data = {
            "category_id": test_budget_item.category_id,  # Categoría ya existente en el presupuesto
            "budgeted_amount": 200.00
        }

        response = await async_client.post(
            f"/budgets/{test_budget.id}/items/",
            json=item_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.json()
        assert "Ya existe un ítem para esta categoría en el presupuesto" in data["detail"]

    @pytest.mark.asyncio
    async def test_update_budget_item_success(self, async_client: AsyncClient, auth_headers, test_budget, test_budget_item):
        """Test actualizar ítem de presupuesto exitoso"""
        update_data = {
            "budgeted_amount": 600.00,
            "notes": "Updated notes"
        }

        response = await async_client.put(
            f"/budgets/{test_budget.id}/items/{test_budget_item.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_budget_item.id
        assert data["budgeted_amount"] == "600.00"
        assert data["notes"] == "Updated notes"

    @pytest.mark.asyncio
    async def test_delete_budget_item_success(self, async_client: AsyncClient, auth_headers, test_budget, test_budget_item):
        """Test eliminar ítem de presupuesto exitoso"""
        response = await async_client.delete(
            f"/budgets/{test_budget.id}/items/{test_budget_item.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_get_budget_comparison(self, async_client: AsyncClient, auth_headers, test_budget, test_budget_item, db_session):
        """Test obtener comparación de presupuesto vs gastos reales"""
        # Crear un gasto en el período del presupuesto
        from app.models.expense import Expense
        expense = Expense(
            user_id=test_budget.user_id,
            category_id=test_budget_item.category_id,
            amount=200.00,
            description="Test expense",
            date=datetime.now(UTC)
        )
        db_session.add(expense)
        db_session.commit()

        response = await async_client.get(
            f"/budgets/{test_budget.id}/comparison",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_budgeted" in data
        assert "total_spent" in data
        assert "total_remaining" in data
        assert "percentage_used" in data
        assert "comparisons" in data
        assert len(data["comparisons"]) >= 1

        # Verificar comparación del ítem
        comparison = data["comparisons"][0]
        assert comparison["budget_id"] == test_budget.id
        assert comparison["category_id"] == test_budget_item.category_id
        assert comparison["budgeted_amount"] == str(test_budget_item.budgeted_amount)
        assert comparison["spent_amount"] == "200.0"
        assert comparison["remaining_amount"] == str(float(test_budget_item.budgeted_amount) - 200.00)

    @pytest.mark.asyncio
    async def test_budget_without_authentication(self, async_client: AsyncClient):
        """Test acceso sin autenticación"""
        response = await async_client.get("/budgets/")

        assert response.status_code == 403  # Forbidden

    @pytest.mark.asyncio
    async def test_create_budget_empty_items(self, async_client: AsyncClient, auth_headers):
        """Test crear presupuesto sin ítems"""
        budget_data = {
            "name": "Empty Budget",
            "start_date": date.today().isoformat(),
            "end_date": date.today().replace(day=28).isoformat(),
            "currency": "COP",
            "budget_items": []
        }

        response = await async_client.post(
            "/budgets/",
            json=budget_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["total_budgeted"] == "0.00"
        assert len(data["budget_items"]) == 0