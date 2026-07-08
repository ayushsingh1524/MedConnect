import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.doctor import Doctor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_db():
    async with AsyncSessionLocal() as session:
        # Check if we already have doctors
        from sqlalchemy import select
        result = await session.execute(select(Doctor).limit(1))
        if result.scalar_one_or_none():
            logger.info("Database already seeded with doctors.")
            return

        doctors_data = [
            Doctor(name="Dr. Sarah Jenkins", specialty="Cardiology", hospital="Mercy General", city="San Francisco", email="s.jenkins@mercy.org", phone="(555) 123-4567"),
            Doctor(name="Dr. Michael Chen", specialty="Neurology", hospital="SF Medical Center", city="San Francisco", email="m.chen@sfmed.org", phone="(555) 987-6543"),
            Doctor(name="Dr. Emily Davis", specialty="Endocrinology", hospital="Valley Health", city="San Jose", email="e.davis@valley.org", phone="(555) 456-7890"),
        ]

        session.add_all(doctors_data)
        await session.commit()
        logger.info("Seeded database with initial doctors.")

if __name__ == "__main__":
    asyncio.run(seed_db())
