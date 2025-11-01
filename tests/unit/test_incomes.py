import pytest
from httpx import AsyncClient
from datetime import datetime
from sqlalchemy.orm import Session

class TestIncomeEndpoints:
    """Tests para endpoints de ingresos"""

    @pytest.mark.asyncio
    async def test_create_income_success(self, async_client: AsyncClient, auth_headers, db_session: Session):
        """Test crear ingreso exitoso"""
        income_data = {
            "amount": 2500.00,
            "description": "Monthly salary",
            "source": "Job",
            "date": datetime.utcnow().isoformat(),
            "is_recurring": True,
            "recurring_frequency": "monthly",
            "category": "Primary",
            "notes": "Main income source"
        }

        response = await async_client.post(
            "/incomes/",
            json=income_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 2500.00
        assert data["description"] == "Monthly salary"
        assert data["source"] == "Job"
        assert data["is_recurring"] is True
        assert data["recurring_frequency"] == "monthly"
        assert data["category"] == "Primary"
        assert data["notes"] == "Main income source"
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_income_minimal_data(self, async_client: AsyncClient, auth_headers):
        """Test crear ingreso con datos mínimos"""
        income_data = {
            "amount": 100.00,
            "description": "Freelance project",
            "source": "Freelance",
            "date": datetime.utcnow().isoformat()
        }

        response = await async_client.post(
            "/incomes/",
            json=income_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 100.00
        assert data["description"] == "Freelance project"
        assert data["source"] == "Freelance"
        assert data["is_recurring"] is False  # Default value
        assert data["category"] is None  # Optional field

    @pytest.mark.asyncio
    async def test_create_income_invalid_amount(self, async_client: AsyncClient, auth_headers):
        """Test crear ingreso con monto inválido"""
        income_data = {
            "amount": 0,  # Monto cero
            "description": "Test income",
            "source": "Test",
            "date": datetime.utcnow().isoformat()
        }

        response = await async_client.post(
            "/incomes/",
            json=income_data,
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_incomes_list(self, async_client: AsyncClient, auth_headers, test_income):
        """Test obtener lista de ingresos"""
        response = await async_client.get("/incomes/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Verificar que el ingreso de prueba está en la lista
        income_found = False
        for income in data:
            if income["id"] == test_income.id:
                income_found = True
                assert income["amount"] == test_income.amount
                assert income["description"] == test_income.description
                assert income["source"] == test_income.source
                break

        assert income_found, "Test income not found in response"

    @pytest.mark.asyncio
    async def test_get_incomes_with_filters(self, async_client: AsyncClient, auth_headers, test_income):
        """Test obtener ingresos con filtros"""
        response = await async_client.get(
            f"/incomes/?source={test_income.source}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Todos los ingresos deberían ser de la fuente especificada
        for income in data:
            assert income["source"] == test_income.source

    @pytest.mark.asyncio
    async def test_get_income_by_id(self, async_client: AsyncClient, auth_headers, test_income):
        """Test obtener ingreso por ID"""
        response = await async_client.get(
            f"/incomes/{test_income.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_income.id
        assert data["amount"] == test_income.amount
        assert data["description"] == test_income.description
        assert data["source"] == test_income.source

    @pytest.mark.asyncio
    async def test_get_income_not_found(self, async_client: AsyncClient, auth_headers):
        """Test obtener ingreso inexistente"""
        response = await async_client.get("/incomes/99999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "Ingreso no encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_update_income_success(self, async_client: AsyncClient, auth_headers, test_income):
        """Test actualizar ingreso exitoso"""
        update_data = {
            "amount": 1500.00,
            "description": "Updated salary",
            "source": "Job Updated",
            "category": "Primary Updated"
        }

        response = await async_client.put(
            f"/incomes/{test_income.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_income.id
        assert data["amount"] == 1500.00
        assert data["description"] == "Updated salary"
        assert data["source"] == "Job Updated"
        assert data["category"] == "Primary Updated"

    @pytest.mark.asyncio
    async def test_update_income_partial(self, async_client: AsyncClient, auth_headers, test_income):
        """Test actualizar ingreso parcialmente"""
        update_data = {
            "amount": 2000.00
        }

        response = await async_client.put(
            f"/incomes/{test_income.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_income.id
        assert data["amount"] == 2000.00
        # Otros campos deberían mantenerse igual
        assert data["description"] == test_income.description
        assert data["source"] == test_income.source

    @pytest.mark.asyncio
    async def test_update_income_not_found(self, async_client: AsyncClient, auth_headers):
        """Test actualizar ingreso inexistente"""
        update_data = {
            "amount": 1000.00,
            "description": "Updated description"
        }

        response = await async_client.put(
            "/incomes/99999",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert "Ingreso no encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_delete_income_success(self, async_client: AsyncClient, auth_headers, test_income):
        """Test eliminar ingreso exitoso"""
        response = await async_client.delete(
            f"/incomes/{test_income.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verificar que el ingreso fue eliminado
        get_response = await async_client.get(
            f"/incomes/{test_income.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_income_not_found(self, async_client: AsyncClient, auth_headers):
        """Test eliminar ingreso inexistente"""
        response = await async_client.delete("/incomes/99999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "Ingreso no encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_incomes_summary_by_source(self, async_client: AsyncClient, auth_headers, test_income):
        """Test obtener resumen de ingresos por fuente"""
        response = await async_client.get("/incomes/summary/source", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Buscar el resumen de la fuente del ingreso de prueba
        source_found = False
        for summary in data:
            if summary["source"] == test_income.source:
                source_found = True
                assert "total_amount" in summary
                assert "count" in summary
                assert summary["total_amount"] > 0
                assert summary["count"] >= 1
                break

        assert source_found, f"Source {test_income.source} not found in summary"

    @pytest.mark.asyncio
    async def test_incomes_pagination(self, async_client: AsyncClient, auth_headers, db_session):
        """Test paginación de ingresos"""
        # Crear múltiples ingresos
        from app.models.income import Income

        for i in range(5):
            income = Income(
                user_id=1,  # Asumiendo que test_user tiene id=1
                amount=100.00 + i * 50,
                description=f"Test income {i}",
                source="Test Source",
                date=datetime.utcnow()
            )
            db_session.add(income)
        db_session.commit()

        # Test primera página
        response = await async_client.get("/incomes/?skip=0&limit=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

        # Test segunda página
        response = await async_client.get("/incomes/?skip=3&limit=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0  # Puede ser 0 si no hay más ingresos

    @pytest.mark.asyncio
    async def test_income_without_authentication(self, async_client: AsyncClient):
        """Test acceso sin autenticación"""
        response = await async_client.get("/incomes/")

        assert response.status_code == 403  # Forbidden

    @pytest.mark.asyncio
    async def test_create_income_with_tags(self, async_client: AsyncClient, auth_headers):
        """Test crear ingreso con etiquetas"""
        income_data = {
            "amount": 500.00,
            "description": "Side hustle income",
            "source": "Side Hustle",
            "date": datetime.utcnow().isoformat(),
            "tags": '["side-hustle", "extra-income"]'
        }

        response = await async_client.post(
            "/incomes/",
            json=income_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["tags"] == '["side-hustle", "extra-income"]'