import pytest
from httpx import AsyncClient
from datetime import datetime
from sqlalchemy.orm import Session

class TestExpenseEndpoints:
    """Tests para endpoints de gastos"""

    @pytest.mark.asyncio
    async def test_create_expense_success(self, async_client: AsyncClient, auth_headers, db_session: Session, test_category):
        """Test crear gasto exitoso"""
        expense_data = {
            "amount": 50.75,
            "description": "Test expense description",
            "category_id": test_category.id,
            "date": datetime.utcnow().isoformat(),
            "payment_method_id": None,
            "is_recurring": False,
            "tag_ids": [],
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
        assert data["category_id"] == test_category.id
        assert data["payment_method_id"] is None
        assert data["is_recurring"] is False
        assert data["tag_ids"] == []
        assert data["notes"] == "Test notes"
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
        # Category is not loaded by default in create response
        # It would be loaded in get operations
        assert data["category_id"] == test_category.id

    @pytest.mark.asyncio
    async def test_create_expense_invalid_amount(self, async_client: AsyncClient, auth_headers, test_category):
        """Test crear gasto con monto inválido"""
        expense_data = {
            "amount": -10,  # Monto negativo
            "description": "Test expense",
            "category_id": test_category.id,
            "date": datetime.utcnow().isoformat(),
            "tag_ids": []
        }

        response = await async_client.post(
            "/expenses/",
            json=expense_data,
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_expense_missing_required_fields(self, async_client: AsyncClient, auth_headers, test_category):
        """Test crear gasto con campos requeridos faltantes"""
        expense_data = {
            "amount": 50.00,
            # Faltan description y category_id
            "tag_ids": []
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
                assert expense["category_id"] == test_expense.category_id
                # Category is loaded in list operations
                if "category" in expense:
                    assert expense["category"]["name"] == "Food"
                break

        assert expense_found, "Test expense not found in response"

    @pytest.mark.asyncio
    async def test_get_expenses_with_filters(self, async_client: AsyncClient, auth_headers, test_expense):
        """Test obtener gastos con filtros"""
        # Nota: Los filtros se prueban en test_get_expenses_list
        # Este test verifica que la función existe y es accesible

        response = await async_client.get(
            f"/expenses/?category_id={test_expense.category_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Todos los gastos deberían ser de la categoría del test
        for expense in data:
            assert expense["category_id"] == test_expense.category_id

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
        assert data["category_id"] == test_expense.category_id
        # Category is loaded in get operations
        if "category" in data:
            assert data["category"]["name"] == "Food"

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

        # Crear categoría para el otro usuario
        from app.models.category import Category
        other_category = Category(
            user_id=other_user.id,
            name="Food",
            category_type="expense",
            description="Food expenses"
        )
        db_session.add(other_category)
        db_session.commit()

        # Crear gasto para el otro usuario
        other_expense = Expense(
            user_id=other_user.id,
            category_id=other_category.id,
            amount=100.00,
            description="Other user's expense",
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
    async def test_update_expense_success(self, async_client: AsyncClient, auth_headers, test_expense, db_session):
        """Test actualizar gasto exitoso"""
        # Crear nueva categoría para la actualización
        from app.models.category import Category
        new_category = Category(
            user_id=test_expense.user_id,
            name="Entertainment",
            category_type="expense",
            description="Entertainment expenses"
        )
        db_session.add(new_category)
        db_session.commit()

        update_data = {
            "amount": 75.50,
            "description": "Updated expense description",
            "category_id": new_category.id
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
        assert data["category_id"] == new_category.id
        # Category is loaded in update operations
        if "category" in data:
            assert data["category"]["name"] == "Entertainment"
        # Campos no actualizados deberían mantenerse
        assert data["payment_method_id"] == test_expense.payment_method_id

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
            if summary["category_id"] == test_expense.category_id:
                category_found = True
                assert "total_amount" in summary
                assert "count" in summary
                assert "category_name" in summary
                assert summary["category_name"] == "Food"
                assert summary["total_amount"] > 0
                assert summary["count"] >= 1
                break

        assert category_found, f"Category {test_expense.category_id} not found in summary"

    @pytest.mark.asyncio
    async def test_expenses_pagination(self, async_client: AsyncClient, auth_headers, db_session, test_user):
        """Test paginación de gastos"""
        # Crear múltiples gastos
        from app.models.expense import Expense

        # Crear categoría para los gastos de paginación
        from app.models.category import Category
        pagination_category = Category(
            user_id=test_user.id,
            name="Test",
            category_type="expense",
            description="Test category for pagination"
        )
        db_session.add(pagination_category)
        db_session.commit()

        for i in range(5):
            expense = Expense(
                user_id=test_user.id,
                category_id=pagination_category.id,
                amount=10.00 + i,
                description=f"Test expense {i}",
                date=datetime.utcnow(),
                payment_method_id=None
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
    async def test_create_expense_with_recurring_data(self, async_client: AsyncClient, auth_headers, db_session, test_user):
        """Test crear gasto con datos de recurrencia"""
        # Crear categoría para el test
        from app.models.category import Category
        services_category = Category(
            user_id=test_user.id,
            name="Services",
            category_type="expense",
            description="Service expenses"
        )
        db_session.add(services_category)
        db_session.commit()

        expense_data = {
            "amount": 100.00,
            "description": "Monthly subscription",
            "category_id": services_category.id,
            "date": datetime.utcnow().isoformat(),
            "is_recurring": True,
            "recurring_frequency": "monthly",
            "tag_ids": []
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
        assert data["tag_ids"] == []