import pytest
from httpx import AsyncClient
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from app.models.expense import Expense
from app.models.income import Income
from app.models.budget import Budget
from app.models.category import Category

class TestDashboardEndpoints:
    """Tests para endpoints del dashboard"""

    @pytest.mark.asyncio
    async def test_get_dashboard_summary_success(self, async_client: AsyncClient, auth_headers, db_session: Session, test_user):
        """Test obtener resumen del dashboard exitoso"""
        # 1. Crear categorías para el usuario
        cat_expense = Category(user_id=test_user.id, name="Test Expense Cat", category_type="expense")
        cat_income = Category(user_id=test_user.id, name="Test Income Cat", category_type="income")
        db_session.add_all([cat_expense, cat_income])
        db_session.flush()

        # 2. Crear algunos datos de prueba
        # Gastos
        expense1 = Expense(user_id=test_user.id, amount=1000.0, description="Gasto 1", date=datetime.now(UTC), category_id=cat_expense.id)
        expense2 = Expense(user_id=test_user.id, amount=500.0, description="Gasto 2", date=datetime.now(UTC), category_id=cat_expense.id)
        db_session.add_all([expense1, expense2])
        
        # Ingresos
        income1 = Income(user_id=test_user.id, amount=3000.0, description="Ingreso 1", source="Trabajo", date=datetime.now(UTC), category_id=cat_income.id)
        db_session.add(income1)
        
        # Presupuesto activo
        budget1 = Budget(user_id=test_user.id, name="Presupuesto 1", start_date=datetime.now(UTC), end_date=datetime.now(UTC), is_active=True, total_budgeted=1000.0)
        db_session.add(budget1)
        
        db_session.commit()

        # 3. Llamar al endpoint
        response = await async_client.get("/dashboard/summary", headers=auth_headers)

        # 4. Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_expenses"] == 1500.0
        assert data["total_incomes"] == 3000.0
        assert data["balance"] == 1500.0
        assert data["active_budgets_count"] >= 1
        assert len(data["recent_transactions"]) >= 3
        
        # Verificar que las transacciones están ordenadas por fecha (desc)
        dates = [datetime.fromisoformat(t["date"].replace("Z", "+00:00")) for t in data["recent_transactions"]]
        assert all(dates[i] >= dates[i+1] for i in range(len(dates)-1))
        
        # Verificar que los nombres de las categorías están presentes
        for transaction in data["recent_transactions"]:
            assert transaction["category_name"] is not None
            if transaction["type"] == "expense":
                assert transaction["category_name"] == "Test Expense Cat"
            else:
                assert transaction["category_name"] == "Test Income Cat"
