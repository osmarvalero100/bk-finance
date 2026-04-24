#!/usr/bin/env python
"""Seed script to populate demo data in the database.

Usage:
    python scripts/seed_demo.py

This script populates the database with realistic demo data for testing.
Run this after running migrations to create the database structure.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import SessionLocal


def seed_demo_data():
    """Seed demo data for testing and demonstration purposes."""
    db = SessionLocal()
    # Configuración para hashear contraseñas con Argon2

    try:
        existing_users = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        if existing_users > 0:
            print("Database already has data, skipping seed...")
            print("To re-seed, first delete all data from the database.")
            return

        print("Seeding demo data...")

        user_id = 1
        db.execute(
            text("""
            INSERT INTO users (id, email, username, hashed_password, full_name, is_active, created_at, updated_at)
            VALUES (1, 'demo@bkfinance.com', 'demo_user', '$argon2id$v=19$m=65536,t=3,p=4$HNuCRbLRGjzFgp4MICMgZQ$xi22UoQF2tEW2egLsbQ0OhlydBCZsa43yElZlTVyNOM', 'Demo User', 1, NOW(), NOW())
        """)
        )

        now = datetime.now()

        expense_categories = [
            (
                1,
                "Supermercado",
                "Gastos en supermercado y restaurantes",
                "#FF5733",
                "🛒",
            ),
            (2, "Transporte", "Gasolina, taxi, Uber", "#33FF57", "🚎"),
            (3, "Vivienda", "Alquiler, Reaparaciones, Muebles", "#3357FF", "🏠"),
            (
                4,
                "Servicios Públicos",
                "Teléfono, internet, suscripciones",
                "#FF33F5",
                "🔌",
            ),
            (5, "Entretenimiento", "Cine, streaming, juegos", "#FFB533", "🎬"),
            (6, "Salud", "Médico, farmacia, seguro", "#33FFF5", "🩺"),
            (7, "Educación", "Cursos, libros, membresías", "#5733FF", "👨‍🎓"),
            (
                8,
                "Ropa y Accesorios",
                "Vestimenta y accesorios personales",
                "#F533FF",
                "🛍️",
            ),
            (9, "Regalos", "Cumpleaños, bodas, otras ocasiones", "#FF3357", "🎁"),
            (
                10,
                "Mascotas",
                "Comida, veterinario, accesorios para mascotas",
                "#3380FF",
                "🐶",
            ),
        ]

        for cat in expense_categories:
            db.execute(
                text("""
                INSERT INTO categories (id, user_id, name, description, color, icon, is_default, category_type, is_active, created_at, updated_at)
                VALUES (:id, :user_id, :name, :desc, :color, :icon, 1, 'expense', 1, :created, :updated)
            """),
                {
                    "id": cat[0],
                    "user_id": user_id,
                    "name": cat[1],
                    "desc": cat[2],
                    "color": cat[3],
                    "icon": cat[4],
                    "created": now,
                    "updated": now,
                },
            )

        payment_methods = [
            (
                1,
                "Efectivo",
                "Dinero en efectivo",
                "cash",
                None,
                "",
                "#28A745",
                "💵",
            ),
            (
                2,
                "Tarjeta de Crédito Bancolombia",
                "Tarjeta de crédito Visa",
                "credit_card",
                "Bancolombia",
                "4521",
                "#FFD700",
                "💳",
            ),
            (
                3,
                "Tarjeta de Débito Davivienda",
                "Tarjeta de débito Mastercard",
                "debit_card",
                "Davivienda",
                "8823",
                "#DC143C",
                "💳",
            ),
            (
                4,
                "Nequi",
                "Billetera digital Nequi",
                "digital_wallet",
                "Nequi",
                "****",
                "#8A2BE2",
                "💳",
            ),
            (
                5,
                "Daviplata",
                "Billetera digital Daviplata",
                "digital_wallet",
                "Daviplata",
                "****",
                "#FF4500",
                "💳",
            ),
            (
                6,
                "Cuenta de Ahorros Davivienda",
                "Cuenta de ahorros",
                "bank_transfer",
                "Davivienda",
                "5521",
                "#1E90FF",
                "💳",
            ),
        ]

        for pm in payment_methods:
            db.execute(
                text("""
                INSERT INTO payment_methods (id, user_id, name, description, payment_type, institution, account_number, color, icon, is_default, is_active, created_at, updated_at)
                VALUES (:id, :user_id, :name, :desc, :type, :inst, :acct, :color, :icon, 1, 1, :created, :updated)
            """),
                {
                    "id": pm[0],
                    "user_id": user_id,
                    "name": pm[1],
                    "desc": pm[2],
                    "type": pm[3],
                    "inst": pm[4],
                    "acct": pm[5],
                    "color": pm[6],
                    "icon": pm[7],
                    "created": now,
                    "updated": now,
                },
            )

        tags = [
            (
                1,
                "Ara",
                "Supermercado",
                "#fa8c0b",
                "",
            ),
            (
                2,
                "D1",
                "Supermercado",
                "#eb0b2b",
                "",
            ),
            (
                3,
                "Exito",
                "Supermercado",
                "#ffe800",
                "",
            ),
            (4, "Koaj", "Ropa", "#000000", ""),
            (5, "Droguerías", "Compras de droguería", "#28A745", ""),
            (6, "Taxis y Apps 🚘", "Taxi, Uber, Yango, Indriver, Didi", "#17A2B8", ""),
        ]

        for tag in tags:
            db.execute(
                text("""
                INSERT INTO tags (id, user_id, name, description, color, icon, is_active, created_at, updated_at)
                VALUES (:id, :user_id, :name, :desc, :color, :icon, 1, :created, :updated)
            """),
                {
                    "id": tag[0],
                    "user_id": user_id,
                    "name": tag[1],
                    "desc": tag[2],
                    "color": tag[3],
                    "icon": tag[4],
                    "created": now,
                    "updated": now,
                },
            )

        expenses_data = [
            (
                1,
                user_id,
                1,
                1,
                250000.00,
                "Mercado semanal",
                now - timedelta(days=2),
                0,
                None,
                "Supermercado Éxito",
            ),
            (
                2,
                user_id,
                2,
                2,
                45000.00,
                "Comida del gato",
                now - timedelta(days=5),
                0,
                None,
                "Alimento para mascotas",
            ),
            (
                3,
                user_id,
                1,
                1,
                85000.00,
                "Restaurante",
                now - timedelta(days=7),
                0,
                None,
                "Restaurant local",
            ),
            (
                4,
                user_id,
                4,
                4,
                89000.00,
                "Internet mes",
                now - timedelta(days=10),
                1,
                "monthly",
                "Claro Fibra",
            ),
            (
                5,
                user_id,
                7,
                4,
                120000.00,
                "Curso Udemy",
                now - timedelta(days=12),
                0,
                None,
                "Udemy",
            ),
            (
                6,
                user_id,
                1,
                1,
                320000.00,
                "Mercado quincena",
                now - timedelta(days=20),
                0,
                None,
                "Supermercado Éxito",
            ),
            (
                7,
                user_id,
                3,
                6,
                450000.00,
                "Arriendo abril",
                now - timedelta(days=22),
                1,
                "monthly",
                "Casa propia",
            ),
            (
                8,
                user_id,
                3,
                6,
                180000.00,
                "Servicios públicos",
                now - timedelta(days=25),
                1,
                "monthly",
                "Varios",
            ),
            (
                9,
                user_id,
                5,
                2,
                45000.00,
                "Netflix",
                now - timedelta(days=28),
                1,
                "monthly",
                "Netflix",
            ),
            (
                10,
                user_id,
                6,
                3,
                85000.00,
                "Medicamentos",
                now - timedelta(days=30),
                0,
                None,
                "Farmacia",
            ),
            (
                11,
                user_id,
                2,
                4,
                55000.00,
                "Taxi aeropuerto",
                now - timedelta(days=45),
                0,
                None,
                "Taxi",
            ),
            (
                12,
                user_id,
                1,
                2,
                180000.00,
                "Cena especial",
                now - timedelta(days=50),
                0,
                None,
                "Restaurante fino",
            ),
            (
                13,
                user_id,
                8,
                3,
                250000.00,
                "Zapatos nuevos",
                now - timedelta(days=55),
                0,
                None,
                "Zapatomania",
            ),
            (
                14,
                user_id,
                5,
                4,
                35000.00,
                "Spotify",
                now - timedelta(days=70),
                1,
                "monthly",
                "Spotify",
            ),
            (
                15,
                user_id,
                10,
                3,
                120000.00,
                "Veterinario mascota",
                now - timedelta(days=80),
                0,
                None,
                "Clínica veterinaria",
            ),
            (
                16,
                user_id,
                9,
                2,
                150000.00,
                "Regalo Navidad",
                now - timedelta(days=120),
                0,
                None,
                "Regalos",
            ),
            (
                17,
                user_id,
                5,
                2,
                65000.00,
                "Cine y snacks",
                now - timedelta(days=90),
                0,
                None,
                "Cine Colombia",
            ),
            (
                18,
                user_id,
                4,
                4,
                55000.00,
                "Celular plan",
                now - timedelta(days=100),
                1,
                "monthly",
                "Tigo",
            ),
            (
                19,
                user_id,
                1,
                4,
                95000.00,
                "Dominos pizza",
                now - timedelta(days=110),
                0,
                None,
                "Dominos",
            ),
            (
                20,
                user_id,
                2,
                4,
                38000.00,
                "Transporte Uber",
                now - timedelta(days=115),
                0,
                None,
                "Uber",
            ),
        ]

        for exp in expenses_data:
            db.execute(
                text("""
                INSERT INTO expenses (id, user_id, category_id, payment_method_id, amount, description, date, is_recurring, recurring_frequency, notes, created_at, updated_at)
                VALUES (:id, :user_id, :cat_id, :pm_id, :amount, :desc, :date, :recurring, :freq, :notes, :created, :updated)
            """),
                {
                    "id": exp[0],
                    "user_id": exp[1],
                    "cat_id": exp[2],
                    "pm_id": exp[3],
                    "amount": exp[4],
                    "desc": exp[5],
                    "date": exp[6],
                    "recurring": exp[7],
                    "freq": exp[8],
                    "notes": exp[9],
                    "created": now,
                    "updated": now,
                },
            )

        incomes_data = [
            (
                1,
                user_id,
                3500000.00,
                "Salario abril",
                "Empleo",
                now - timedelta(days=1),
                1,
                "monthly",
                "Pago de nómina Bancolombia",
            ),
            (
                2,
                user_id,
                3500000.00,
                "Salario marzo",
                "Empreo",
                now - timedelta(days=30),
                1,
                "monthly",
                "Pago de nómina Bancolombia",
            ),
            (
                3,
                user_id,
                800000.00,
                "Diseño logo cliente",
                "Freelance",
                now - timedelta(days=25),
                0,
                None,
                "Freelance proyecto",
            ),
            (
                4,
                user_id,
                3500000.00,
                "Salario febrero",
                "Empleo",
                now - timedelta(days=58),
                1,
                "monthly",
                "Pago de nómina Bancolombia",
            ),
            (
                5,
                user_id,
                450000.00,
                "Desarrollo web",
                "Freelance",
                now - timedelta(days=50),
                0,
                None,
                "Freelance proyecto",
            ),
            (
                6,
                user_id,
                150000.00,
                "Dividendos acciones",
                "Inversión en bolsa",
                now - timedelta(days=55),
                0,
                None,
                "Dividendos trimestre",
            ),
            (
                7,
                user_id,
                3500000.00,
                "Salario enero",
                "Empleo",
                now - timedelta(days=89),
                1,
                "monthly",
                "Pago de nómina Bancolombia",
            ),
            (
                8,
                user_id,
                1200000.00,
                "App desarrollo",
                "Freelance",
                now - timedelta(days=80),
                0,
                None,
                "Freelance proyecto",
            ),
            (
                9,
                user_id,
                3500000.00,
                "Salario diciembre",
                "Empleo",
                now - timedelta(days=120),
                1,
                "monthly",
                "Pago de nómina Bancolombia",
            ),
            (
                10,
                user_id,
                180000.00,
                "Dividendos acciones",
                "Inversión en bolsa",
                now - timedelta(days=115),
                0,
                None,
                "Dividendos trimestre",
            ),
        ]

        for inc in incomes_data:
            db.execute(
                text("""
                INSERT INTO incomes (id, user_id, amount, description, source, date, is_recurring, recurring_frequency, notes, created_at, updated_at)
                VALUES (:id, :user_id, :amount, :desc, :source, :date, :recurring, :freq, :notes, :created, :updated)
            """),
                {
                    "id": inc[0],
                    "user_id": inc[1],
                    "amount": inc[2],
                    "desc": inc[3],
                    "source": inc[4],
                    "date": inc[5],
                    "recurring": inc[6],
                    "freq": inc[7],
                    "notes": inc[8],
                    "created": now,
                    "updated": now,
                },
            )

        # Asignar etiquetas a algunos gastos (expense_tags)
        expense_tags_data = [
            (1, 1, 2),  # expense 1 -> tag 2 (Planificado)
            (2, 2, 1),  # expense 2 -> tag 1 (Urgente)
            (3, 3, 3),  # expense 3 -> tag 3 (Ocasional)
            (4, 4, 2),  # expense 4 -> tag 2 (Planificado)
            (5, 5, 2),  # expense 5 -> tag 2 (Planificado)
            (9, 9, 1),  # expense 9 -> tag 3 (Ocasional)
            (10, 10, 3),  # expense 10 -> tag 1 (Urgente)
            (11, 11, 5),  # expense 11 -> tag 5 (Viaje)
            (12, 12, 3),  # expense 12 -> tag 3 (Ocasional)
        ]

        for et in expense_tags_data:
            db.execute(
                text("""
                INSERT INTO expense_tags (id, expense_id, tag_id, created_at)
                VALUES (:id, :expense_id, :tag_id, :created)
                """),
                {"id": et[0], "expense_id": et[1], "tag_id": et[2], "created": now},
            )

        investments_data = [
            (
                "Acciones Bancolombia",
                "BCOLOMBIA",
                "stocks",
                15000000.00,
                16200000.00,
                now - timedelta(days=365),
                100,
                150000.00,
                162000.00,
                "FB",
                500000.00,
                0,
                0,
                None,
                "low",
                "finanzas",
                "Inversión a largo plazo",
            ),
            (
                "CDT Davivienda",
                None,
                "bonds",
                5000000.00,
                5350000.00,
                now - timedelta(days=180),
                None,
                None,
                None,
                "Davivienda",
                150000.00,
                0,
                0,
                now + timedelta(days=185),
                "low",
                "finanzas",
                "CDT a 6 meses",
            ),
            (
                "Bitcoin",
                "BTC",
                "crypto",
                2000000.00,
                4500000.00,
                now - timedelta(days=400),
                0.02,
                100000000.00,
                225000000.00,
                "Binance",
                100000.00,
                0,
                0,
                None,
                "high",
                "tecnología",
                "Inversión en criptomonedas",
            ),
        ]

        for i, inv in enumerate(investments_data, 1):
            db.execute(
                text("""
                INSERT INTO investments (id, user_id, name, symbol, investment_type, amount_invested, current_value, purchase_date, quantity, purchase_price, current_price, broker_platform, fees, taxes, dividends_earned, is_active, maturity_date, risk_level, sector, notes, created_at, updated_at)
                VALUES (:id, :user_id, :name, :symbol, :type, :invested, :current, :purchase, :qty, :price, :cur_price, :broker, :fees, :taxes, :dividends, 1, :maturity, :risk, :sector, :notes, :created, :updated)
            """),
                {
                    "id": i,
                    "user_id": user_id,
                    "name": inv[0],
                    "symbol": inv[1],
                    "type": inv[2],
                    "invested": inv[3],
                    "current": inv[4],
                    "purchase": inv[5],
                    "qty": inv[6],
                    "price": inv[7],
                    "cur_price": inv[8],
                    "broker": inv[9],
                    "fees": inv[10],
                    "taxes": inv[11],
                    "dividends": inv[12],
                    "maturity": inv[13],
                    "risk": inv[14],
                    "sector": inv[15],
                    "notes": inv[16],
                    "created": now,
                    "updated": now,
                },
            )

        financial_products_data = [
            (
                "Cuenta de Ahorros Davivienda",
                "savings_account",
                "Davivienda",
                "5521",
                8500000.00,
                3.5,
                0,
                0,
                None,
                None,
                None,
                None,
                now - timedelta(days=730),
                "COP",
                "Ahorros principal",
            ),
            (
                "Tarjeta de Crédito Visa Bancolombia",
                "credit_card",
                "Bancolombia",
                "4521",
                450000.00,
                2.5,
                0,
                15000,
                5000000.00,
                4600000.00,
                15,
                150000,
                now - timedelta(days=500),
                "COP",
                "Límite $5.000.000",
            ),
            (
                "Cuenta Corriente Bancolombia",
                "checking_account",
                "Bancolombia",
                "8821",
                1200000.00,
                0.5,
                0,
                0,
                None,
                None,
                None,
                None,
                now - timedelta(days=1000),
                "COP",
                "Cuenta empresarial",
            ),
        ]

        for i, fp in enumerate(financial_products_data, 1):
            db.execute(
                text("""
                INSERT INTO financial_products (id, user_id, name, product_type, institution, account_number, balance, interest_rate, minimum_balance, monthly_fee, credit_limit, available_credit, payment_due_date, minimum_payment, is_active, opening_date, maturity_date, currency, notes, created_at, updated_at)
                VALUES (:id, :user_id, :name, :type, :inst, :acct, :balance, :rate, :min_bal, :fee, :limit, :available, :due, :min_pay, 1, :opening, :maturity, :currency, :notes, :created, :updated)
            """),
                {
                    "id": i,
                    "user_id": user_id,
                    "name": fp[0],
                    "type": fp[1],
                    "inst": fp[2],
                    "acct": fp[3],
                    "balance": fp[4],
                    "rate": fp[5],
                    "min_bal": fp[6],
                    "fee": fp[7],
                    "limit": fp[8],
                    "available": fp[9],
                    "due": fp[10],
                    "min_pay": fp[11],
                    "opening": fp[12],
                    "maturity": None,
                    "currency": fp[13],
                    "notes": fp[14],
                    "created": now,
                    "updated": now,
                },
            )

        debts_data = [
            (
                "Tarjeta de Crédito Visa",
                "credit_card",
                "Bancolombia",
                3500000.00,
                1850000.00,
                2.5,
                85000.00,
                20,
                now - timedelta(days=400),
                "COP",
                "Saldo rotativo",
            ),
        ]

        for i, debt in enumerate(debts_data, 1):
            db.execute(
                text("""
                INSERT INTO debts (id, user_id, name, debt_type, lender, original_amount, current_balance, interest_rate, minimum_payment, payment_due_date, loan_start_date, expected_end_date, is_paid_off, paid_off_date, currency, collateral, notes, created_at, updated_at)
                VALUES (:id, :user_id, :name, :type, :lender, :original, :balance, :rate, :min_pay, :due, :start, :end, 0, NULL, :currency, :collateral, :notes, :created, :updated)
            """),
                {
                    "id": i,
                    "user_id": user_id,
                    "name": debt[0],
                    "type": debt[1],
                    "lender": debt[2],
                    "original": debt[3],
                    "balance": debt[4],
                    "rate": debt[5],
                    "min_pay": debt[6],
                    "due": debt[7],
                    "start": debt[8],
                    "end": None,
                    "currency": debt[9],
                    "collateral": None,
                    "notes": debt[10],
                    "created": now,
                    "updated": now,
                },
            )

        budget_id = 1
        db.execute(
            text("""
            INSERT INTO budgets (id, user_id, name, description, start_date, end_date, total_budgeted, total_spent, currency, is_active, created_at, updated_at)
            VALUES (:id, :user_id, 'Presupuesto Abril 2025', 'Gastos mensuales abril', :start, :end, :budgeted, :spent, 'COP', 1, :created, :updated)
        """),
            {
                "id": budget_id,
                "user_id": user_id,
                "start": datetime(2025, 4, 1).date(),
                "end": datetime(2025, 4, 30).date(),
                "budgeted": 2500000.00,
                "spent": 1150000.00,
                "created": now,
                "updated": now,
            },
        )

        budget_items = [
            (1, budget_id, 1, 600000.00, 380000.00),
            (2, budget_id, 2, 200000.00, 85000.00),
            (3, budget_id, 3, 500000.00, 450000.00),
            (4, budget_id, 4, 150000.00, 89000.00),
            (5, budget_id, 5, 150000.00, 85000.00),
            (6, budget_id, 6, 100000.00, 85000.00),
        ]

        for item in budget_items:
            db.execute(
                text("""
                INSERT INTO budget_items (id, budget_id, category_id, budgeted_amount, spent_amount, notes, created_at, updated_at)
                VALUES (:id, :budget_id, :cat_id, :budgeted, :spent, NULL, :created, :updated)
            """),
                {
                    "id": item[0],
                    "budget_id": item[1],
                    "cat_id": item[2],
                    "budgeted": item[3],
                    "spent": item[4],
                    "created": now,
                    "updated": now,
                },
            )

        db.commit()

        print("Demo data seeded successfully!")
        print("Username: demo_user")
        print("Password: password123")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
