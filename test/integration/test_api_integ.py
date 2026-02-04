import pytest
from src.core.database import SessionLocal, engine
from sqlalchemy import text

def test_db_connection():
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
    except Exception as e:
        pytest.fail(f"Database connection failed: {str(e)}")
    finally:
        db.close()
