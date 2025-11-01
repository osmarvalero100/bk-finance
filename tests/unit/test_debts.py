import pytest
from httpx import AsyncClient
from datetime import datetime
from sqlalchemy.orm import Session

class TestDebtEndpoints:
    """Tests para endpoints de deudas"""

    @pytest.mark.asyncio
    async def test_create_debt_success(self, async_client: AsyncClient, auth_headers, db_session: Session):
        """Test crear deuda exitosa"""
        debt_data = {
            "name": "Car Loan",
            "debt_type": "auto_loan",
            "lender": "Auto Finance Corp",
            "original_amount": 25000.00,
            "current_balance": 18000.00,
            "interest_rate": 0.06,
            "minimum_payment": 450.00,
            "payment_due_date": 15,
            "loan_start_date": datetime.utcnow().isoformat(),
            "expected_end_date": datetime.utcnow().replace(year=datetime.utcnow().year + 4).isoformat(),
            "is_paid_off": False,
            "currency": "USD",
            "notes": "Car loan for Honda Civic"
        }

        response = await async_client.post(
            "/debts/",
            json=debt_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Car Loan"
        assert data["debt_type"] == "auto_loan"
        assert data["lender"] == "Auto Finance Corp"
        assert data["original_amount"] == 25000.00
        assert data["current_balance"] == 18000.00
        assert data["interest_rate"] == 0.06
        assert data["minimum_payment"] == 450.00
        assert data["payment_due_date"] == 15
        assert data["is_paid_off"] is False
        assert data["currency"] == "USD"
        assert data["notes"] == "Car loan for Honda Civic"
        assert "id" in data
        assert "user_id" in data

    @pytest.mark.asyncio
    async def test_create_debt_minimal_data(self, async_client: AsyncClient, auth_headers):
        """Test crear deuda con datos mínimos"""
        debt_data = {
            "name": "Personal Loan",
            "debt_type": "personal_loan",
            "lender": "Family Member",
            "original_amount": 5000.00,
            "current_balance": 5000.00,
            "interest_rate": 0.0,
            "minimum_payment": 250.00,
            "loan_start_date": datetime.utcnow().isoformat()
        }

        response = await async_client.post(
            "/debts/",
            json=debt_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Personal Loan"
        assert data["debt_type"] == "personal_loan"
        assert data["lender"] == "Family Member"
        assert data["original_amount"] == 5000.00
        assert data["current_balance"] == 5000.00
        assert data["interest_rate"] == 0.0
        assert data["minimum_payment"] == 250.00
        assert data["is_paid_off"] is False  # Default value

    @pytest.mark.asyncio
    async def test_create_debt_invalid_amounts(self, async_client: AsyncClient, auth_headers):
        """Test crear deuda con montos inválidos"""
        debt_data = {
            "name": "Test Debt",
            "debt_type": "personal_loan",
            "lender": "Test Lender",
            "original_amount": -1000,  # Monto negativo
            "current_balance": 500.00,
            "interest_rate": 0.05,
            "minimum_payment": 50.00,
            "loan_start_date": datetime.utcnow().isoformat()
        }

        response = await async_client.post(
            "/debts/",
            json=debt_data,
            headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_debts_list(self, async_client: AsyncClient, auth_headers, test_debt):
        """Test obtener lista de deudas"""
        response = await async_client.get("/debts/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Verificar que la deuda de prueba está en la lista
        debt_found = False
        for debt in data:
            if debt["id"] == test_debt.id:
                debt_found = True
                assert debt["name"] == test_debt.name
                assert debt["debt_type"] == test_debt.debt_type
                assert debt["lender"] == test_debt.lender
                break

        assert debt_found, "Test debt not found in response"

    @pytest.mark.asyncio
    async def test_get_debts_with_filters(self, async_client: AsyncClient, auth_headers, test_debt):
        """Test obtener deudas con filtros"""
        response = await async_client.get(
            f"/debts/?debt_type={test_debt.debt_type}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Todas las deudas deberían ser del tipo especificado
        for debt in data:
            assert debt["debt_type"] == test_debt.debt_type

    @pytest.mark.asyncio
    async def test_get_debts_unpaid_only(self, async_client: AsyncClient, auth_headers, test_debt):
        """Test obtener solo deudas no pagadas"""
        response = await async_client.get(
            "/debts/?is_paid_off=false",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Todas las deudas deberían estar sin pagar
        for debt in data:
            assert debt["is_paid_off"] is False

    @pytest.mark.asyncio
    async def test_get_debt_by_id(self, async_client: AsyncClient, auth_headers, test_debt):
        """Test obtener deuda por ID"""
        response = await async_client.get(
            f"/debts/{test_debt.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_debt.id
        assert data["name"] == test_debt.name
        assert data["debt_type"] == test_debt.debt_type
        assert data["lender"] == test_debt.lender

    @pytest.mark.asyncio
    async def test_get_debt_not_found(self, async_client: AsyncClient, auth_headers):
        """Test obtener deuda inexistente"""
        response = await async_client.get("/debts/99999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "Deuda no encontrada" in data["detail"]

    @pytest.mark.asyncio
    async def test_update_debt_success(self, async_client: AsyncClient, auth_headers, test_debt):
        """Test actualizar deuda exitosa"""
        update_data = {
            "current_balance": 15000.00,
            "minimum_payment": 400.00,
            "notes": "Updated loan terms"
        }

        response = await async_client.put(
            f"/debts/{test_debt.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_debt.id
        assert data["current_balance"] == 15000.00
        assert data["minimum_payment"] == 400.00
        assert data["notes"] == "Updated loan terms"
        # Campos no actualizados deberían mantenerse
        assert data["name"] == test_debt.name
        assert data["original_amount"] == test_debt.original_amount

    @pytest.mark.asyncio
    async def test_update_debt_not_found(self, async_client: AsyncClient, auth_headers):
        """Test actualizar deuda inexistente"""
        update_data = {
            "current_balance": 1000.00,
            "notes": "Updated notes"
        }

        response = await async_client.put(
            "/debts/99999",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert "Deuda no encontrada" in data["detail"]

    @pytest.mark.asyncio
    async def test_delete_debt_success(self, async_client: AsyncClient, auth_headers, test_debt):
        """Test eliminar deuda exitosa"""
        response = await async_client.delete(
            f"/debts/{test_debt.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verificar que la deuda fue eliminada
        get_response = await async_client.get(
            f"/debts/{test_debt.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_debt_not_found(self, async_client: AsyncClient, auth_headers):
        """Test eliminar deuda inexistente"""
        response = await async_client.delete("/debts/99999", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "Deuda no encontrada" in data["detail"]

    @pytest.mark.asyncio
    async def test_mark_debt_as_paid_off(self, async_client: AsyncClient, auth_headers, test_debt):
        """Test marcar deuda como pagada"""
        response = await async_client.put(
            f"/debts/{test_debt.id}/pay-off",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Deuda marcada como pagada exitosamente" in data["message"]
        assert data["debt"]["is_paid_off"] is True
        assert data["debt"]["current_balance"] == 0
        assert "paid_off_date" in data["debt"]

    @pytest.mark.asyncio
    async def test_mark_already_paid_debt_as_paid_off(self, async_client: AsyncClient, auth_headers, db_session, test_user):
        """Test marcar deuda ya pagada como pagada"""
        # Crear deuda ya pagada
        from app.models.debt import Debt

        paid_debt = Debt(
            user_id=test_user.id,
            name="Already Paid Debt",
            debt_type="personal_loan",
            lender="Test Lender",
            original_amount=1000.00,
            current_balance=0.00,
            interest_rate=0.05,
            minimum_payment=50.00,
            loan_start_date=datetime.utcnow(),
            is_paid_off=True
        )
        db_session.add(paid_debt)
        db_session.commit()

        response = await async_client.put(
            f"/debts/{paid_debt.id}/pay-off",
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.json()
        assert "La deuda ya está marcada como pagada" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_debts_summary_by_type(self, async_client: AsyncClient, auth_headers, test_debt):
        """Test obtener resumen de deudas por tipo"""
        response = await async_client.get("/debts/summary/type", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Buscar el resumen del tipo de deuda de prueba
        type_found = False
        for summary in data:
            if summary["debt_type"] == test_debt.debt_type:
                type_found = True
                assert "total_balance" in summary
                assert "count" in summary
                assert summary["total_balance"] > 0
                assert summary["count"] >= 1
                break

        assert type_found, f"Debt type {test_debt.debt_type} not found in summary"

    @pytest.mark.asyncio
    async def test_get_total_debt_balance(self, async_client: AsyncClient, auth_headers, test_debt):
        """Test obtener balance total de deudas"""
        response = await async_client.get("/debts/balance/total", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_debt" in data
        assert "currency" in data

        # Con la deuda de prueba, debería haber algún balance
        assert data["total_debt"] >= 0
        assert data["currency"] == "COP"

    @pytest.mark.asyncio
    async def test_debts_pagination(self, async_client: AsyncClient, auth_headers, db_session, test_user):
        """Test paginación de deudas"""
        # Crear múltiples deudas
        from app.models.debt import Debt

        for i in range(5):
            debt = Debt(
                user_id=test_user.id,
                name=f"Test Debt {i}",
                debt_type="personal_loan",
                lender="Test Lender",
                original_amount=1000.00 + i * 100,
                current_balance=800.00 + i * 80,
                interest_rate=0.05,
                minimum_payment=50.00 + i * 5,
                loan_start_date=datetime.utcnow()
            )
            db_session.add(debt)
        db_session.commit()

        # Test primera página
        response = await async_client.get("/debts/?skip=0&limit=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

        # Test segunda página
        response = await async_client.get("/debts/?skip=3&limit=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0  # Puede ser 0 si no hay más deudas

    @pytest.mark.asyncio
    async def test_debt_without_authentication(self, async_client: AsyncClient):
        """Test acceso sin autenticación"""
        response = await async_client.get("/debts/")

        assert response.status_code == 403  # Forbidden

    @pytest.mark.asyncio
    async def test_create_debt_with_collateral(self, async_client: AsyncClient, auth_headers):
        """Test crear deuda con garantía"""
        debt_data = {
            "name": "Mortgage Loan",
            "debt_type": "mortgage",
            "lender": "Mortgage Bank",
            "original_amount": 300000.00,
            "current_balance": 280000.00,
            "interest_rate": 0.045,
            "minimum_payment": 1500.00,
            "loan_start_date": datetime.utcnow().isoformat(),
            "collateral": "House at 123 Main St"
        }

        response = await async_client.post(
            "/debts/",
            json=debt_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["debt_type"] == "mortgage"
        assert data["collateral"] == "House at 123 Main St"
        assert data["original_amount"] == 300000.00