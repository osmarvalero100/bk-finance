from app.utils.auth import get_password_hash, verify_password

results = []

# Test 1: long ASCII password
try:
    pw1 = 'a' * 200
    h1 = get_password_hash(pw1)
    ok1 = verify_password(pw1, h1)
    results.append(("long_ascii", ok1, None))
except Exception as e:
    results.append(("long_ascii", False, repr(e)))

# Test 2: long multibyte password (emoji)
try:
    pw2 = '😊' * 40
    h2 = get_password_hash(pw2)
    ok2 = verify_password(pw2, h2)
    results.append(("long_multibyte", ok2, None))
except Exception as e:
    results.append(("long_multibyte", False, repr(e)))

# Test 3: None should raise ValueError
try:
    get_password_hash(None)
    results.append(("none_raises", False, "no exception raised"))
except Exception as e:
    results.append(("none_raises", True, type(e).__name__ + ": " + str(e)))

for name, ok, err in results:
    if ok:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}: {err}")

# Exit code
if all(ok for _, ok, _ in results):
    raise SystemExit(0)
else:
    raise SystemExit(2)
