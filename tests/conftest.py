import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from datetime import datetime, timedelta

# Configurar variables de entorno para tests
os.environ["DATABASE_URL"] = "sqlite:///./test_finance.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DEBUG"] = "True"

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.expense import Expense
from app.models.income import Income
from app.models.investment import Investment
from app.models.financial_product import FinancialProduct
from app.models.debt import Debt
from app.models.category import Category
from app.utils.auth import get_password_hash, create_access_token

# Configurar base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_finance.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas de prueba
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Sobrescribir la dependencia de base de datos para tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def db_session():
    """Fixture para sesión de base de datos"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(db_session):
    """Crear usuario de prueba"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]

    # Crear usuario mock directamente usando get_password_hash (Argon2)
    pw = "testpassword123"
    user = User(
        email=f"test_{unique_id}@example.com",
        username=f"testuser_{unique_id}",
        hashed_password=get_password_hash(pw),
        full_name=f"Test User {unique_id}",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    """Crear headers de autenticación para tests"""
    access_token = create_access_token(
        data={"sub": test_user.username},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def test_category(db_session, test_user):
    """Crear categoría de prueba"""
    category = Category(
        user_id=test_user.id,
        name="Food",
        category_type="expense",
        description="Food and dining expenses"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category

@pytest.fixture
def test_expense(db_session, test_user, test_category):
    """Crear gasto de prueba"""
    expense = Expense(
        user_id=test_user.id,
        category_id=test_category.id,
        amount=100.50,
        description="Test expense",
        date=datetime.utcnow(),
        payment_method_id=None
    )
    db_session.add(expense)
    db_session.commit()
    db_session.refresh(expense)
    return expense

@pytest.fixture
def test_income_category(db_session, test_user):
    """Crear categoría de ingreso de prueba"""
    category = Category(
        user_id=test_user.id,
        name="Salary",
        category_type="income",
        description="Salary income"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category

@pytest.fixture
def test_income(db_session, test_user, test_income_category):
    """Crear ingreso de prueba"""
    income = Income(
        user_id=test_user.id,
        category_id=test_income_category.id,
        amount=1000.00,
        description="Test income",
        source="Salary",
        date=datetime.utcnow()
    )
    db_session.add(income)
    db_session.commit()
    db_session.refresh(income)
    return income

@pytest.fixture
def test_investment(db_session, test_user):
    """Crear inversión de prueba"""
    investment = Investment(
        user_id=test_user.id,
        name="Test Stock",
        symbol="TEST",
        investment_type="stocks",
        amount_invested=1000.00,
        current_value=1100.00,
        purchase_date=datetime.utcnow(),
        quantity=10,
        purchase_price=100.00,
        current_price=110.00,
        broker_platform="Test Broker",
        is_active=True
    )
    db_session.add(investment)
    db_session.commit()
    db_session.refresh(investment)
    return investment

@pytest.fixture
def test_financial_product(db_session, test_user):
    """Crear producto financiero de prueba"""
    product = FinancialProduct(
        user_id=test_user.id,
        name="Test Savings Account",
        product_type="savings_account",
        institution="Test Bank",
        account_number="1234567890",
        balance=5000.00,
        interest_rate=0.02,
        is_active=True,
        opening_date=datetime.utcnow()
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product

@pytest.fixture
def test_debt(db_session, test_user):
    """Crear deuda de prueba"""
    debt = Debt(
        user_id=test_user.id,
        name="Test Loan",
        debt_type="personal_loan",
        lender="Test Bank",
        original_amount=10000.00,
        current_balance=8000.00,
        interest_rate=0.05,
        minimum_payment=500.00,
        loan_start_date=datetime.utcnow(),
        is_paid_off=False
    )
    db_session.add(debt)
    db_session.commit()
    db_session.refresh(debt)
    return debt

@pytest_asyncio.fixture
async def async_client():
    """Cliente HTTP async para tests"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(autouse=True)
def clean_db():
    """Limpiar base de datos después de cada test"""
    yield
    # Nota: En un ambiente real, podrías limpiar todas las tablas aquí
    # Por simplicidad, usaremos una base de datos en memoria o recrearemos las tablas

# Configuración para pytest-asyncio
pytest_plugins = ("pytest_asyncio",)