import pytest
from httpx import AsyncClient
from datetime import datetime
from sqlalchemy.orm import Session

class TestInvestmentEndpoints:
    """Tests para endpoints de inversiones"""

    @pytest.mark.asyncio
    async def test_create_investment_success(self, async_client: AsyncClient, auth_headers, db_session: Session):
        """Test crear inversión exitosa"""
        investment_data = {
            "name": "Apple Inc.",
            "symbol": "AAPL",
            "investment_type": "stocks",
            "amount_invested": 5000.00,
            "current_value": 5500.00,
            "purchase_date": datetime.utcnow().isoformat(),
            "quantity": 50,
            "purchase_price": 100.00,
            "current_price": 110.00,
            "broker_platform": "Interactive Brokers",
            "fees": 5.00,
            "taxes": 0.00,
            "dividends_earned": 25.00,
            "is_active": True,
            "risk_level": "medium",
            "sector": "Technology",
            "notes": "Long-term investment"
        }

        response = await async_client.post(
            "/investments/",
            json=investment_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Apple Inc."
        assert data["symbol"] == "AAPL"
        assert data["investment_type"] == "stocks"
        assert data["amount_invested"] == 5000.00
        assert data["current_value"] == 5500.00
        assert data["quantity"] == 50
        assert data["purchase_price"] == 100.00
        assert data["current_price"] == 110.00
        assert data["broker_platform"] == "Interactive Brokers"
        assert data["is_active"] is True
        assert data["risk_level"] == "medium"
        assert data["sector"] == "Technology"
        assert data["notes"] == "Long-term investment"
        assert "id" in data
        assert "user_id" in data

    @pytest.mark.asyncio
    async def test_create_investment_minimal_data(self, async_client: AsyncClient, auth_headers):
        """Test crear inversión con datos mínimos"""
        investment_data = {
            "name": "Bitcoin",
            "investment_type": "crypto",
            "amount_invested": 1000.00,
            "purchase_date": datetime.utcnow().isoformat()
        }

        response = await async_client.post(
            "/investments/",
            json=investment_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Bitcoin"
        assert data["investment_type"] == "crypto"
        assert data["amount_invested"] == 1000.00
        assert data["is_active"] is True  # Default value
        assert data["current_value"] is None  # Optional field

    @pytest.mark.asyncio
    async def test_create_investment_invalid_amount(self, async_client: AsyncClient, auth_headers):
        """Test crear inversión con monto inválido"""
        investment_data = {
            "name": "Test Investment",
            "investment_type": "stocks",
            "amount_invested": -100,  # Monto negativo
            "purchase_date": datetime.utcnow().isoformat()
        }

        response = await async_client.post(
            "/investments/",
            json=investment_data,
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_investments_list(self, async_client: AsyncClient, auth_headers, test_investment):
        """Test obtener lista de inversiones"""
        response = await async_client.get("/investments/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Verificar que la inversión de prueba está en la lista
        investment_found = False
        for investment in data:
            if investment["id"] == test_investment.id:
                investment_found = True
                assert investment["name"] == test_investment.name
                assert investment["investment_type"] == test_investment.investment_type
                assert investment["amount_invested"] == test_investment.amount_invested
                break

        assert investment_found, "Test investment not found in response"

    @pytest.mark.asyncio
    async def test_get_investments_with_filters(self, async_client: AsyncClient, auth_headers, test_investment):
        """Test obtener inversiones con filtros"""
        response = await async_client.get(
            f"/investments/?investment_type={test_investment.investment_type}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Todas las inversiones deberían ser del tipo especificado
        for investment in data:
            assert investment["investment_type"] == test_investment.investment_type

    @pytest.mark.asyncio
    async def test_get_investments_active_only(self, async_client: AsyncClient, auth_headers, test_investment):
        """Test obtener solo inversiones activas"""
        response = await async_client.get(
            "/investments/?is_active=true",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Todas las inversiones deberían estar activas
        for investment in data:
            assert investment["is_active"] is True

    @pytest.mark.asyncio
    async def test_get_investment_by_id(self, async_client: AsyncClient, auth_headers, test_investment):
        """Test obtener inversión por ID"""
        response = await async_client.get(
            f"/investments/{test_investment.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_investment.id
        assert data["name"] == test_investment.name
        assert data["investment_type"] == test_investment.investment_type
        assert data["amount_invested"] == test_investment.amount_invested

    @pytest.mark.asyncio
    async def test_get_investment_not_found(self, async_client: AsyncClient, auth_headers):
        """Test obtener inversión inexistente"""
        response = await async_client.get("/investments/99999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "Inversión no encontrada" in data["detail"]

    @pytest.mark.asyncio
    async def test_update_investment_success(self, async_client: AsyncClient, auth_headers, test_investment):
        """Test actualizar inversión exitosa"""
        update_data = {
            "current_value": 1200.00,
            "current_price": 120.00,
            "dividends_earned": 50.00,
            "notes": "Updated notes"
        }

        response = await async_client.put(
            f"/investments/{test_investment.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_investment.id
        assert data["current_value"] == 1200.00
        assert data["current_price"] == 120.00
        assert data["dividends_earned"] == 50.00
        assert data["notes"] == "Updated notes"
        # Campos no actualizados deberían mantenerse
        assert data["name"] == test_investment.name
        assert data["amount_invested"] == test_investment.amount_invested

    @pytest.mark.asyncio
    async def test_update_investment_not_found(self, async_client: AsyncClient, auth_headers):
        """Test actualizar inversión inexistente"""
        update_data = {
            "current_value": 1500.00,
            "notes": "Updated notes"
        }

        response = await async_client.put(
            "/investments/99999",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert "Inversión no encontrada" in data["detail"]

    @pytest.mark.asyncio
    async def test_delete_investment_success(self, async_client: AsyncClient, auth_headers, test_investment):
        """Test eliminar inversión exitosa"""
        response = await async_client.delete(
            f"/investments/{test_investment.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verificar que la inversión fue eliminada
        get_response = await async_client.get(
            f"/investments/{test_investment.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_investment_not_found(self, async_client: AsyncClient, auth_headers):
        """Test eliminar inversión inexistente"""
        response = await async_client.delete("/investments/99999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "Inversión no encontrada" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_investments_summary_by_type(self, async_client: AsyncClient, auth_headers, test_investment):
        """Test obtener resumen de inversiones por tipo"""
        response = await async_client.get("/investments/summary/type", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Buscar el resumen del tipo de inversión de prueba
        type_found = False
        for summary in data:
            if summary["investment_type"] == test_investment.investment_type:
                type_found = True
                assert "total_invested" in summary
                assert "total_current_value" in summary
                assert "count" in summary
                assert summary["total_invested"] > 0
                assert summary["count"] >= 1
                break

        assert type_found, f"Investment type {test_investment.investment_type} not found in summary"

    @pytest.mark.asyncio
    async def test_get_total_investment_performance(self, async_client: AsyncClient, auth_headers, test_investment):
        """Test obtener rendimiento total de inversiones"""
        response = await async_client.get("/investments/performance/total", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_invested" in data
        assert "total_current_value" in data
        assert "total_performance" in data
        assert "performance_percentage" in data

        # Con la inversión de prueba, debería haber algún rendimiento
        assert data["total_invested"] > 0
        assert data["total_current_value"] >= data["total_invested"]

    @pytest.mark.asyncio
    async def test_investments_pagination(self, async_client: AsyncClient, auth_headers, db_session):
        """Test paginación de inversiones"""
        # Crear múltiples inversiones
        from app.models.investment import Investment

        for i in range(5):
            investment = Investment(
                user_id=1,  # Asumiendo que test_user tiene id=1
                name=f"Test Investment {i}",
                investment_type="stocks",
                amount_invested=1000.00 + i * 100,
                purchase_date=datetime.utcnow()
            )
            db_session.add(investment)
        db_session.commit()

        # Test primera página
        response = await async_client.get("/investments/?skip=0&limit=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

        # Test segunda página
        response = await async_client.get("/investments/?skip=3&limit=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0  # Puede ser 0 si no hay más inversiones

    @pytest.mark.asyncio
    async def test_investment_without_authentication(self, async_client: AsyncClient):
        """Test acceso sin autenticación"""
        response = await async_client.get("/investments/")

        assert response.status_code == 403  # Forbidden

    @pytest.mark.asyncio
    async def test_create_investment_with_maturity_date(self, async_client: AsyncClient, auth_headers):
        """Test crear inversión con fecha de vencimiento"""
        future_date = datetime.utcnow().replace(year=datetime.utcnow().year + 5)
        investment_data = {
            "name": "5-Year Bond",
            "investment_type": "bonds",
            "amount_invested": 10000.00,
            "purchase_date": datetime.utcnow().isoformat(),
            "maturity_date": future_date.isoformat(),
            "risk_level": "low"
        }

        response = await async_client.post(
            "/investments/",
            json=investment_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["maturity_date"] == future_date.isoformat()
        assert data["risk_level"] == "low"