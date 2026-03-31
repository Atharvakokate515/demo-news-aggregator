import sys
from app.runner import run_scrapers
from app.daily_runner import run_daily_pipeline


def ensure_database_setup():
    """
    Automatically create database tables if they don't exist.
    Safe to run multiple times - won't affect existing tables.
    """
    try:
        print("🔍 Checking database setup...")
        from app.database.create_tables import Base
        from app.database.connection import engine
        
        Base.metadata.create_all(engine)
        print("✅ Database tables are ready\n")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\nTroubleshooting:")
        print("1. Check Docker is running: docker ps")
        print("2. Start database: cd docker && docker-compose up -d")
        print("3. Verify .env file has database credentials")
        sys.exit(1)


def main():
    ensure_database_setup()  # <-- This is the only line added to main()
    
    if len(sys.argv) != 3:
        print("Usage: python main.py <hours_back> <top_n_articles>")
        sys.exit(1)

    hours_back = int(sys.argv[1])
    top_n = int(sys.argv[2])

    run_daily_pipeline(hours=hours_back, top_n=top_n)


if __name__ == "__main__":
    main()
