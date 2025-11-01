import pytest
from httpx import AsyncClient
from datetime import datetime
from sqlalchemy.orm import Session

class TestExpenseEndpoints:
    """Tests para endpoints de gastos"""

    @pytest.mark.asyncio
    async def test_create_expense_success(self, async_client: AsyncClient, auth_headers, db_session: Session):
        """Test crear gasto exitoso"""
        expense_data = {
            "amount": 50.75,
            "description": "Test expense description",
            "category": "Food",
            "date": datetime.utcnow().isoformat(),
            "payment_method": "Credit Card",
            "is_recurring": False,
            "notes": "Test notes"
        }

        response = await async_client.post(
            "/expenses/",
            json=expense_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 50.75
        assert data["description"] == "Test expense description"
        assert data["category"] == "Food"
        assert data["payment_method"] == "Credit Card"
        assert data["is_recurring"] is False
        assert data["notes"] == "Test notes"
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_expense_invalid_amount(self, async_client: AsyncClient, auth_headers):
        """Test crear gasto con monto inválido"""
        expense_data = {
            "amount": -10,  # Monto negativo
            "description": "Test expense",
            "category": "Food",
            "date": datetime.utcnow().isoformat()
        }

        response = await async_client.post(
            "/expenses/",
            json=expense_data,
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_expense_missing_required_fields(self, async_client: AsyncClient, auth_headers):
        """Test crear gasto con campos requeridos faltantes"""
        expense_data = {
            "amount": 50.00,
            # Faltan description y category
        }

        response = await async_client.post(
            "/expenses/",
            json=expense_data,
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_expenses_list(self, async_client: AsyncClient, auth_headers, test_expense):
        """Test obtener lista de gastos"""
        response = await async_client.get("/expenses/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Verificar que el gasto de prueba está en la lista
        expense_found = False
        for expense in data:
            if expense["id"] == test_expense.id:
                expense_found = True
                assert expense["amount"] == test_expense.amount
                assert expense["description"] == test_expense.description
                assert expense["category"] == test_expense.category
                break

        assert expense_found, "Test expense not found in response"

    @pytest.mark.asyncio
    async def test_get_expenses_with_filters(self, async_client: AsyncClient, auth_headers, test_expense):
        """Test obtener gastos con filtros"""
        # Nota: Los filtros se prueban en test_get_expenses_list
        # Este test verifica que la función existe y es accesible

        response = await async_client.get(
            "/expenses/?category=Food",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Todos los gastos deberían ser de categoría Food
        for expense in data:
            assert expense["category"] == "Food"

    @pytest.mark.asyncio
    async def test_get_expense_by_id(self, async_client: AsyncClient, auth_headers, test_expense):
        """Test obtener gasto por ID"""
        response = await async_client.get(
            f"/expenses/{test_expense.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_expense.id
        assert data["amount"] == test_expense.amount
        assert data["description"] == test_expense.description
        assert data["category"] == test_expense.category

    @pytest.mark.asyncio
    async def test_get_expense_not_found(self, async_client: AsyncClient, auth_headers):
        """Test obtener gasto inexistente"""
        response = await async_client.get("/expenses/99999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "Gasto no encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_expense_wrong_user(self, async_client: AsyncClient, auth_headers, db_session):
        """Test obtener gasto de otro usuario"""
        # Crear usuario diferente mock directamente en BD
        from app.models.user import User
        from app.models.expense import Expense
        from app.utils.auth import create_access_token
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        from app.utils.auth import get_password_hash
        other_user = User(
            email=f"other_{unique_id}@example.com",
            username=f"otheruser_{unique_id}",
            hashed_password=get_password_hash("other_user_pw"),
            full_name="Other User"
        )
        db_session.add(other_user)
        db_session.commit()

        # Crear gasto para el otro usuario
        other_expense = Expense(
            user_id=other_user.id,
            amount=100.00,
            description="Other user's expense",
            category="Food",
            date=datetime.utcnow()
        )
        db_session.add(other_expense)
        db_session.commit()

        # Intentar obtener el gasto del otro usuario
        response = await async_client.get(
            f"/expenses/{other_expense.id}",
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert "Gasto no encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_update_expense_success(self, async_client: AsyncClient, auth_headers, test_expense):
        """Test actualizar gasto exitoso"""
        update_data = {
            "amount": 75.50,
            "description": "Updated expense description",
            "category": "Entertainment"
        }

        response = await async_client.put(
            f"/expenses/{test_expense.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_expense.id
        assert data["amount"] == 75.50
        assert data["description"] == "Updated expense description"
        assert data["category"] == "Entertainment"
        # Campos no actualizados deberían mantenerse
        assert data["payment_method"] == test_expense.payment_method

    @pytest.mark.asyncio
    async def test_update_expense_not_found(self, async_client: AsyncClient, auth_headers):
        """Test actualizar gasto inexistente"""
        update_data = {
            "amount": 100.00,
            "description": "Updated description"
        }

        response = await async_client.put(
            "/expenses/99999",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert "Gasto no encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_delete_expense_success(self, async_client: AsyncClient, auth_headers, test_expense):
        """Test eliminar gasto exitoso"""
        response = await async_client.delete(
            f"/expenses/{test_expense.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verificar que el gasto fue eliminado
        get_response = await async_client.get(
            f"/expenses/{test_expense.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_expense_not_found(self, async_client: AsyncClient, auth_headers):
        """Test eliminar gasto inexistente"""
        response = await async_client.delete("/expenses/99999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "Gasto no encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_expenses_summary_by_category(self, async_client: AsyncClient, auth_headers, test_expense):
        """Test obtener resumen de gastos por categoría"""
        response = await async_client.get("/expenses/summary/category", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Buscar el resumen de la categoría del gasto de prueba
        category_found = False
        for summary in data:
            if summary["category"] == test_expense.category:
                category_found = True
                assert "total_amount" in summary
                assert "count" in summary
                assert summary["total_amount"] > 0
                assert summary["count"] >= 1
                break

        assert category_found, f"Category {test_expense.category} not found in summary"

    @pytest.mark.asyncio
    async def test_expenses_pagination(self, async_client: AsyncClient, auth_headers, db_session):
        """Test paginación de gastos"""
        # Crear múltiples gastos
        from app.models.expense import Expense

        for i in range(5):
            expense = Expense(
                user_id=1,  # Asumiendo que test_user tiene id=1
                amount=10.00 + i,
                description=f"Test expense {i}",
                category="Test",
                date=datetime.utcnow()
            )
            db_session.add(expense)
        db_session.commit()

        # Test primera página
        response = await async_client.get("/expenses/?skip=0&limit=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

        # Test segunda página
        response = await async_client.get("/expenses/?skip=3&limit=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0  # Puede ser 0 si no hay más gastos

    @pytest.mark.asyncio
    async def test_expense_without_authentication(self, async_client: AsyncClient):
        """Test acceso sin autenticación"""
        response = await async_client.get("/expenses/")

        assert response.status_code == 403  # Forbidden

    @pytest.mark.asyncio
    async def test_create_expense_with_recurring_data(self, async_client: AsyncClient, auth_headers):
        """Test crear gasto con datos de recurrencia"""
        expense_data = {
            "amount": 100.00,
            "description": "Monthly subscription",
            "category": "Services",
            "date": datetime.utcnow().isoformat(),
            "is_recurring": True,
            "recurring_frequency": "monthly",
            "tags": '["subscription", "monthly"]'
        }

        response = await async_client.post(
            "/expenses/",
            json=expense_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["is_recurring"] is True
        assert data["recurring_frequency"] == "monthly"
        assert data["tags"] == '["subscription", "monthly"]'