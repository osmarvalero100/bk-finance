import traceback
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import TestingSessionLocal
from app.models.user import User
from app.utils.auth import create_access_token
from datetime import datetime

client = TestClient(app)

try:
    db = TestingSessionLocal()
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    mock_user = User(
        email=f"financial_{unique_id}@example.com",
        username=f"financialuser_{unique_id}",
        hashed_password="$2b$12$LQv3c1yqBwlFb4Hnr1QhHJHhIhNNLnuIB.mhHX0Z8v9T0lB8tL8K2",
        full_name=f"Financial User {unique_id}",
        is_active=True
    )
    db.add(mock_user)
    db.commit()
    db.refresh(mock_user)

    token = create_access_token(data={"sub": mock_user.username})
    headers = {"Authorization": f"Bearer {token}"}

    income_data = {
        "amount": 5000.00,
        "description": "Monthly salary",
        "source": "Job",
        "date": datetime.now(UTC).isoformat(),
        "is_recurring": True,
        "recurring_frequency": "monthly",
        "category": "Primary"
    }

    resp = client.post('/incomes/', json=income_data, headers=headers)
    print('status', resp.status_code)
    try:
        print(resp.json())
    except Exception as e:
        print('raw text:', resp.text)

    db.close()
except Exception:
    traceback.print_exc()
