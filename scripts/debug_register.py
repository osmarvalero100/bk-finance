import traceback
from fastapi.testclient import TestClient
from app.main import app
from app.utils.auth import get_password_hash, verify_password
import uuid

client = TestClient(app)

try:
    # Probar hashing
    pw = 'securepass123'
    print('hashing...')
    h = get_password_hash(pw)
    print('hash ok, len:', len(h))
    print(h)

    # Intentar registro
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        'email': f'newuser_{unique_id}@example.com',
        'username': f'newuser_{unique_id}',
        'password': pw,
        'full_name': 'New User'
    }
    resp = client.post('/auth/register', json=user_data)
    print('register status', resp.status_code)
    try:
        print('register body', resp.json())
    except Exception as e:
        print('no json body', e)

    # If created, try login using OAuth2 form
    if resp.status_code in (200,201):
        # login
        login_data = {'username': user_data['username'], 'password': pw}
        r2 = client.post('/auth/login', data=login_data)
        print('login status', r2.status_code)
        try:
            print('login body', r2.json())
        except:
            print('login no json')

    # Also test verify_password against the stored hash if created
    if resp.status_code in (200,201):
        # lookup user in DB
        from app.core.database import TestingSessionLocal
        from app.models.user import User
        db = TestingSessionLocal()
        user = db.query(User).filter(User.username==user_data['username']).first()
        print('db user', user.username, user.email)
        print('stored hash len', len(user.hashed_password))
        print('verify_password ok', verify_password(pw, user.hashed_password))
        db.close()
except Exception:
    traceback.print_exc()
