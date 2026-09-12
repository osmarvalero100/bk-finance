import pytest
from httpx import AsyncClient
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.orm import Session

from app.models.fixed_expense import FixedExpense
from app.models.category import Category
from app.models.expense import Expense
from app.services.email_service import (
    calculate_next_due_date_and_days,
    get_month_due_date,
    check_and_send_due_reminders
)


class TestFixedExpenseEndpoints:
    """Tests para endpoints y servicios de gastos fijos y recordatorios por email"""

    def test_calculate_next_due_date_logic(self):
        """Verifica la lógica de cálculo de fecha de vencimiento y días restantes"""
        ref_date = date(2026, 9, 12)
        
        # Vence el día 15 (dentro de 3 días)
        due_date, days_left = calculate_next_due_date_and_days(15, today=ref_date)
        assert due_date == date(2026, 9, 15)
        assert days_left == 3

        # Vence hoy (día 12)
        due_date_today, days_today = calculate_next_due_date_and_days(12, today=ref_date)
        assert due_date_today == date(2026, 9, 12)
        assert days_today == 0

        # Venció el día 5 (hace una semana), por lo que el próximo vencimiento es el 5 de octubre
        due_date_next_month, days_next_month = calculate_next_due_date_and_days(5, today=ref_date)
        assert due_date_next_month == date(2026, 10, 5)
        assert days_next_month == 23

    def test_get_month_due_date_leap_and_month_end(self):
        """Verifica el ajuste de días para meses con menos de 31 días"""
        # Febrero en año no bisiesto
        feb_date = get_month_due_date(31, 2025, 2)
        assert feb_date == date(2025, 2, 28)

        # Abril tiene 30 días
        apr_date = get_month_due_date(31, 2026, 4)
        assert apr_date == date(2026, 4, 30)

    @pytest.mark.asyncio
    async def test_create_fixed_expense_success(
        self, async_client: AsyncClient, auth_headers, test_category
    ):
        """Test crear gasto fijo exitosamente"""
        payload = {
            "name": "Internet Fibra Óptica",
            "amount": 89900.0,
            "currency": "COP",
            "category_id": test_category.id,
            "due_day": 15,
            "frequency": "monthly",
            "reminder_days_before": 3,
            "email_reminder_enabled": True,
            "is_active": True,
            "notes": "Plan 500 Mbps con Movistar"
        }

        response = await async_client.post(
            "/fixed-expenses/",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Internet Fibra Óptica"
        assert data["amount"] == 89900.0
        assert data["due_day"] == 15
        assert data["reminder_days_before"] == 3
        assert data["email_reminder_enabled"] is True
        assert "next_due_date" in data
        assert "days_until_due" in data
        assert "is_due_soon" in data

    @pytest.mark.asyncio
    async def test_create_fixed_expense_invalid_category(
        self, async_client: AsyncClient, auth_headers
    ):
        """Test crear gasto fijo con categoría inexistente"""
        payload = {
            "name": "Servicio Invalido",
            "amount": 50000.0,
            "category_id": 99999,
            "due_day": 10
        }

        response = await async_client.post(
            "/fixed-expenses/",
            json=payload,
            headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_fixed_expenses_list_and_summary(
        self, async_client: AsyncClient, auth_headers, test_category
    ):
        """Test listar gastos fijos y obtener resumen"""
        # Crear 2 gastos fijos
        await async_client.post(
            "/fixed-expenses/",
            json={
                "name": "Alquiler",
                "amount": 1200000.0,
                "category_id": test_category.id,
                "due_day": 5,
                "email_reminder_enabled": True
            },
            headers=auth_headers
        )
        await async_client.post(
            "/fixed-expenses/",
            json={
                "name": "Spotify Premium",
                "amount": 19900.0,
                "category_id": test_category.id,
                "due_day": 20,
                "email_reminder_enabled": False
            },
            headers=auth_headers
        )

        # Listar
        response = await async_client.get("/fixed-expenses/", headers=auth_headers)
        assert response.status_code == 200
        items = response.json()
        assert len(items) >= 2

        # Resumen
        summary_res = await async_client.get("/fixed-expenses/summary", headers=auth_headers)
        assert summary_res.status_code == 200
        summary_data = summary_res.json()
        assert summary_data["total_monthly_amount"] >= 1219900.0
        assert summary_data["active_count"] >= 2
        assert summary_data["reminders_enabled_count"] >= 1

    @pytest.mark.asyncio
    async def test_update_fixed_expense(
        self, async_client: AsyncClient, auth_headers, test_category
    ):
        """Test actualizar gasto fijo"""
        create_res = await async_client.post(
            "/fixed-expenses/",
            json={
                "name": "Gimnasio",
                "amount": 100000.0,
                "category_id": test_category.id,
                "due_day": 1
            },
            headers=auth_headers
        )
        fe_id = create_res.json()["id"]

        update_res = await async_client.put(
            f"/fixed-expenses/{fe_id}",
            json={"amount": 120000.0, "notes": "Aumento anual"},
            headers=auth_headers
        )
        assert update_res.status_code == 200
        assert update_res.json()["amount"] == 120000.0
        assert update_res.json()["notes"] == "Aumento anual"

    @pytest.mark.asyncio
    async def test_pay_fixed_expense(
        self, async_client: AsyncClient, auth_headers, test_category, db_session: Session
    ):
        """Test registrar pago de gasto fijo en tabla de gastos"""
        create_res = await async_client.post(
            "/fixed-expenses/",
            json={
                "name": "Seguro de Vida",
                "amount": 75000.0,
                "category_id": test_category.id,
                "due_day": 10
            },
            headers=auth_headers
        )
        fe_id = create_res.json()["id"]

        # Pagar
        pay_res = await async_client.post(f"/fixed-expenses/{fe_id}/pay", headers=auth_headers)
        assert pay_res.status_code == 201
        pay_data = pay_res.json()
        assert pay_data["amount"] == 75000.0
        assert "Seguro de Vida" in pay_data["description"]

        # Verificar que se creó en la tabla expenses
        expense = db_session.query(Expense).filter(Expense.id == pay_data["id"]).first()
        assert expense is not None
        assert expense.amount == 75000.0

    @pytest.mark.asyncio
    async def test_send_test_reminder(
        self, async_client: AsyncClient, auth_headers, test_category
    ):
        """Test enviar recordatorio de prueba por email"""
        create_res = await async_client.post(
            "/fixed-expenses/",
            json={
                "name": "Servicio de Luz",
                "amount": 65000.0,
                "category_id": test_category.id,
                "due_day": 18,
                "reminder_days_before": 3,
                "email_reminder_enabled": True
            },
            headers=auth_headers
        )
        fe_id = create_res.json()["id"]

        test_reminder_res = await async_client.post(
            f"/fixed-expenses/{fe_id}/send-test-reminder",
            headers=auth_headers
        )
        assert test_reminder_res.status_code == 200
        data = test_reminder_res.json()
        assert data["success"] is True
        assert "recipient" in data

    @pytest.mark.asyncio
    async def test_check_pending_reminders(
        self, async_client: AsyncClient, auth_headers, test_category, db_session: Session
    ):
        """Test revisión masiva de recordatorios pendientes"""
        today = date.today()
        # Crear un gasto que venza dentro del rango de recordatorio (ej. hoy o en 1 día)
        due_day = today.day

        await async_client.post(
            "/fixed-expenses/",
            json={
                "name": "Gasto que vence hoy",
                "amount": 45000.0,
                "category_id": test_category.id,
                "due_day": due_day,
                "reminder_days_before": 2,
                "email_reminder_enabled": True
            },
            headers=auth_headers
        )

        res = await async_client.post(
            "/fixed-expenses/check-reminders",
            headers=auth_headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["processed"] >= 1
        assert data["reminders_sent"] >= 1

    @pytest.mark.asyncio
    async def test_delete_fixed_expense(
        self, async_client: AsyncClient, auth_headers, test_category
    ):
        """Test eliminar gasto fijo"""
        create_res = await async_client.post(
            "/fixed-expenses/",
            json={
                "name": "Subscripcion a borrar",
                "amount": 15000.0,
                "category_id": test_category.id,
                "due_day": 25
            },
            headers=auth_headers
        )
        fe_id = create_res.json()["id"]

        del_res = await async_client.delete(f"/fixed-expenses/{fe_id}", headers=auth_headers)
        assert del_res.status_code == 204

        get_res = await async_client.get(f"/fixed-expenses/{fe_id}", headers=auth_headers)
        assert get_res.status_code == 404
