import os

os.environ.setdefault("JWT_SECRET", "test-secret-only-not-production")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
