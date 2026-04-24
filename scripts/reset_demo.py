#!/usr/bin/env python
"""Reset script to remove all demo data from the database.

Usage:
    python scripts/reset_demo.py

This script deletes all demo data created by seed_demo.py.
Run this before re-seeding with new data.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import SessionLocal


def reset_demo_data():
    """Remove all demo data from the database."""
    db = SessionLocal()

    try:
        existing_users = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        if existing_users == 0:
            print("No demo data to remove.")
            return

        print("Removing demo data...")

        db.execute(text("DELETE FROM expense_tags"))
        db.execute(text("DELETE FROM income_tags"))
        db.execute(text("DELETE FROM budget_items"))
        db.execute(text("DELETE FROM budgets"))
        db.execute(text("DELETE FROM debts"))
        db.execute(text("DELETE FROM financial_products"))
        db.execute(text("DELETE FROM investments"))
        db.execute(text("DELETE FROM expenses"))
        db.execute(text("DELETE FROM incomes"))
        db.execute(text("DELETE FROM tags"))
        db.execute(text("DELETE FROM payment_methods"))
        db.execute(text("DELETE FROM categories"))
        db.execute(text("DELETE FROM users"))

        db.commit()

        print("Demo data removed successfully!")
        print("You can now run: python scripts/seed_demo.py")

    except Exception as e:
        db.rollback()
        print(f"Error resetting data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset_demo_data()
