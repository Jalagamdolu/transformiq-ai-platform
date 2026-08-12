"""CLI script to seed the database with synthetic enterprise data and research embeddings.

Run from backend directory:
    python seed_db.py
"""

import asyncio
import logging
import sys

from app.db.session import AsyncSessionLocal
from app.seed.novamart import seed_novamart_data
from app.seed.research import seed_research_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_db")


async def main() -> None:
    logger.info("Starting database seeding...")
    async with AsyncSessionLocal() as session:
        org = await seed_novamart_data(session)
        await seed_research_data(session, org)
        logger.info(f"Seeding completed successfully for organisation '{org.name}' (ID: {org.id})!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Seeding failed: {e}", exc_info=True)
        sys.exit(1)
