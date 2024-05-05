import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from database.core import Base, get_sync_engige
from movies.orm import *

Base.metadata.create_all(
    bind=get_sync_engige(),
)
