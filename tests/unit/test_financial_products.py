import pytest
from httpx import AsyncClient
from datetime import datetime
from sqlalchemy.orm import Session

class TestFinancialProductEndpoints:
    """Tests para endpoints de productos financieros"""

    @pytest.mark.asyncio
    async def test_create_financial_product_success(self, async_client: AsyncClient, auth_headers, db_session: Session):
        """Test crear producto financiero exitoso"""
        product_data = {
            "name": "Checking Account",
            "product_type": "checking_account",
            "institution": "Bank of America",
            "account_number": "1234567890",
            "balance": 2500.00,
            "interest_rate": 0.01,
            "minimum_balance": 100.00,
            "monthly_fee": 12.00,
            "is_active": True,
            "opening_date": datetime.utcnow().isoformat(),
            "currency": "USD",
            "notes": "Primary checking account"
        }

        response = await async_client.post(
            "/financial-products/",
            json=product_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Checking Account"
        assert data["product_type"] == "checking_account"
        assert data["institution"] == "Bank of America"
        assert data["account_number"] == "1234567890"
        assert data["balance"] == 2500.00
        assert data["interest_rate"] == 0.01
        assert data["minimum_balance"] == 100.00
        assert data["monthly_fee"] == 12.00
        assert data["is_active"] is True
        assert data["currency"] == "USD"
        assert data["notes"] == "Primary checking account"
        assert "id" in data
        assert "user_id" in data

    @pytest.mark.asyncio
    async def test_create_financial_product_minimal_data(self, async_client: AsyncClient, auth_headers):
        """Test crear producto financiero con datos mínimos"""
        product_data = {
            "name": "Savings Account",
            "product_type": "savings_account",
            "institution": "Chase Bank"
        }

        response = await async_client.post(
            "/financial-products/",
            json=product_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Savings Account"
        assert data["product_type"] == "savings_account"
        assert data["institution"] == "Chase Bank"
        assert data["balance"] == 0  # Default value
        assert data["is_active"] is True  # Default value

    @pytest.mark.asyncio
    async def test_create_financial_product_credit_card(self, async_client: AsyncClient, auth_headers):
        """Test crear producto financiero tipo tarjeta de crédito"""
        product_data = {
            "name": "Premium Credit Card",
            "product_type": "credit_card",
            "institution": "Visa",
            "balance": 1500.00,
            "credit_limit": 5000.00,
            "available_credit": 3500.00,
            "payment_due_date": 15,
            "minimum_payment": 75.00,
            "interest_rate": 0.18
        }

        response = await async_client.post(
            "/financial-products/",
            json=product_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["product_type"] == "credit_card"
        assert data["credit_limit"] == 5000.00
        assert data["available_credit"] == 3500.00
        assert data["payment_due_date"] == 15
        assert data["minimum_payment"] == 75.00

    @pytest.mark.asyncio
    async def test_get_financial_products_list(self, async_client: AsyncClient, auth_headers, test_financial_product):
        """Test obtener lista de productos financieros"""
        response = await async_client.get("/financial-products/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Verificar que el producto financiero de prueba está en la lista
        product_found = False
        for product in data:
            if product["id"] == test_financial_product.id:
                product_found = True
                assert product["name"] == test_financial_product.name
                assert product["product_type"] == test_financial_product.product_type
                assert product["institution"] == test_financial_product.institution
                break

        assert product_found, "Test financial product not found in response"

    @pytest.mark.asyncio
    async def test_get_financial_products_with_filters(self, async_client: AsyncClient, auth_headers, test_financial_product):
        """Test obtener productos financieros con filtros"""
        response = await async_client.get(
            f"/financial-products/?product_type={test_financial_product.product_type}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Todos los productos deberían ser del tipo especificado
        for product in data:
            assert product["product_type"] == test_financial_product.product_type

    @pytest.mark.asyncio
    async def test_get_financial_products_active_only(self, async_client: AsyncClient, auth_headers, test_financial_product):
        """Test obtener solo productos financieros activos"""
        response = await async_client.get(
            "/financial-products/?is_active=true",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Todos los productos deberían estar activos
        for product in data:
            assert product["is_active"] is True

    @pytest.mark.asyncio
    async def test_get_financial_product_by_id(self, async_client: AsyncClient, auth_headers, test_financial_product):
        """Test obtener producto financiero por ID"""
        response = await async_client.get(
            f"/financial-products/{test_financial_product.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_financial_product.id
        assert data["name"] == test_financial_product.name
        assert data["product_type"] == test_financial_product.product_type
        assert data["institution"] == test_financial_product.institution

    @pytest.mark.asyncio
    async def test_get_financial_product_not_found(self, async_client: AsyncClient, auth_headers):
        """Test obtener producto financiero inexistente"""
        response = await async_client.get("/financial-products/99999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "Producto financiero no encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_update_financial_product_success(self, async_client: AsyncClient, auth_headers, test_financial_product):
        """Test actualizar producto financiero exitoso"""
        update_data = {
            "balance": 6000.00,
            "interest_rate": 0.025,
            "notes": "Updated notes for savings account"
        }

        response = await async_client.put(
            f"/financial-products/{test_financial_product.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_financial_product.id
        assert data["balance"] == 6000.00
        assert data["interest_rate"] == 0.025
        assert data["notes"] == "Updated notes for savings account"
        # Campos no actualizados deberían mantenerse
        assert data["name"] == test_financial_product.name
        assert data["institution"] == test_financial_product.institution

    @pytest.mark.asyncio
    async def test_update_financial_product_not_found(self, async_client: AsyncClient, auth_headers):
        """Test actualizar producto financiero inexistente"""
        update_data = {
            "balance": 1000.00,
            "notes": "Updated notes"
        }

        response = await async_client.put(
            "/financial-products/99999",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert "Producto financiero no encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_delete_financial_product_success(self, async_client: AsyncClient, auth_headers, test_financial_product):
        """Test eliminar producto financiero exitoso"""
        response = await async_client.delete(
            f"/financial-products/{test_financial_product.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verificar que el producto fue eliminado
        get_response = await async_client.get(
            f"/financial-products/{test_financial_product.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_financial_product_not_found(self, async_client: AsyncClient, auth_headers):
        """Test eliminar producto financiero inexistente"""
        response = await async_client.delete("/financial-products/99999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "Producto financiero no encontrado" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_financial_products_summary_by_type(self, async_client: AsyncClient, auth_headers, test_financial_product):
        """Test obtener resumen de productos financieros por tipo"""
        response = await async_client.get("/financial-products/summary/type", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Buscar el resumen del tipo de producto de prueba
        type_found = False
        for summary in data:
            if summary["product_type"] == test_financial_product.product_type:
                type_found = True
                assert "total_balance" in summary
                assert "count" in summary
                assert summary["total_balance"] >= 0
                assert summary["count"] >= 1
                break

        assert type_found, f"Product type {test_financial_product.product_type} not found in summary"

    @pytest.mark.asyncio
    async def test_get_total_financial_balance(self, async_client: AsyncClient, auth_headers, test_financial_product):
        """Test obtener balance total de productos financieros"""
        response = await async_client.get("/financial-products/balance/total", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_balance" in data
        assert "currency" in data

        # Con el producto financiero de prueba, debería haber algún balance
        assert data["total_balance"] >= 0
        assert data["currency"] == "COP"

    @pytest.mark.asyncio
    async def test_financial_products_pagination(self, async_client: AsyncClient, auth_headers, db_session):
        """Test paginación de productos financieros"""
        # Crear múltiples productos financieros
        from app.models.financial_product import FinancialProduct

        for i in range(5):
            product = FinancialProduct(
                user_id=1,  # Asumiendo que test_user tiene id=1
                name=f"Test Product {i}",
                product_type="savings_account",
                institution="Test Bank",
                balance=1000.00 + i * 100
            )
            db_session.add(product)
        db_session.commit()

        # Test primera página
        response = await async_client.get("/financial-products/?skip=0&limit=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

        # Test segunda página
        response = await async_client.get("/financial-products/?skip=3&limit=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0  # Puede ser 0 si no hay más productos

    @pytest.mark.asyncio
    async def test_financial_product_without_authentication(self, async_client: AsyncClient):
        """Test acceso sin autenticación"""
        response = await async_client.get("/financial-products/")

        assert response.status_code == 403  # Forbidden

    @pytest.mark.asyncio
    async def test_create_financial_product_loan(self, async_client: AsyncClient, auth_headers):
        """Test crear producto financiero tipo préstamo"""
        future_date = datetime.utcnow().replace(year=datetime.utcnow().year + 10)
        product_data = {
            "name": "Home Mortgage",
            "product_type": "mortgage",
            "institution": "Mortgage Bank",
            "balance": 200000.00,
            "interest_rate": 0.045,
            "monthly_fee": 1200.00,
            "maturity_date": future_date.isoformat(),
            "notes": "30-year fixed mortgage"
        }

        response = await async_client.post(
            "/financial-products/",
            json=product_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["product_type"] == "mortgage"
        assert data["maturity_date"] == future_date.isoformat()
        assert data["monthly_fee"] == 1200.00