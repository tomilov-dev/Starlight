import sys
from pathlib import Path
from abc import abstractmethod, ABCMeta

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from movies.db import MovieDatabase, Base


class DatabaseAdder:
    def __init__(self) -> None:
        self.mvdb = MovieDatabase()

    @abstractmethod
    async def add_all(
        self,
        objects: list[Base],
    ) -> None:
        pass
