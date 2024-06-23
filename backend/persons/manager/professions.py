import sys
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))


from database.manager import DatabaseManager
from persons.orm import ProfessionORM
from services.person_professions import professions


class ProfessionManager(DatabaseManager):
    ORM = ProfessionORM


async def professions_init(professions):
    manager = ProfessionManager()
    await manager.add_batch(professions)


if __name__ == "__main__":
    asyncio.run(professions_init(professions))
