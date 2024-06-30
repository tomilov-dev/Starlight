import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from services.models import PersonProfessionSDM


professions: list[PersonProfessionSDM] = [
    PersonProfessionSDM(imdb_name="self", name_en="Self", name_ru="В роли себя"),
    PersonProfessionSDM(imdb_name="editor", name_en="Editor", name_ru="Монтажер"),
    PersonProfessionSDM(
        imdb_name="miscellaneous", name_en="Miscellaneous", name_ru="Различные работы"
    ),
    PersonProfessionSDM(
        imdb_name="choreographer", name_en="Choreographer", name_ru="Хореограф"
    ),
    PersonProfessionSDM(
        imdb_name="director", name_en="Director", name_ru="Режиссер", crew=True
    ),
    PersonProfessionSDM(
        imdb_name="set_decorator", name_en="Set decorator", name_ru="Декоратор"
    ),
    PersonProfessionSDM(
        imdb_name="assistant", name_en="Assistant", name_ru="Ассистент"
    ),
    PersonProfessionSDM(
        imdb_name="archive_sound",
        name_en="Archive sound",
        name_ru="Специалист по архивным звукозаписям",
    ),
    PersonProfessionSDM(
        imdb_name="casting_director",
        name_en="Casting director",
        name_ru="Кастинг-директор",
    ),
    PersonProfessionSDM(
        imdb_name="talent_agent",
        name_en="Talent agent",
        name_ru="Агент по поиску талантов",
    ),
    PersonProfessionSDM(
        imdb_name="production_manager",
        name_en="Production manager",
        name_ru="Руководитель производства",
    ),
    PersonProfessionSDM(
        imdb_name="production_designer",
        name_en="Production designer",
        name_ru="Художник-постановщик",
    ),
    PersonProfessionSDM(
        imdb_name="art_department",
        name_en="Art department",
        name_ru="Художественное оформление",
    ),
    PersonProfessionSDM(
        imdb_name="podcaster", name_en="Podcaster", name_ru="Подкастер"
    ),
    PersonProfessionSDM(
        imdb_name="production_department",
        name_en="Production department",
        name_ru="Производство",
    ),
    PersonProfessionSDM(
        imdb_name="make_up_department",
        name_en="Make Up department",
        name_ru="Художник-гример",
    ),
    PersonProfessionSDM(
        imdb_name="executive", name_en="Executive", name_ru="Генеральный продюсер"
    ),
    PersonProfessionSDM(
        imdb_name="costume_designer",
        name_en="Costume designer",
        name_ru="Художник по костюмам",
    ),
    PersonProfessionSDM(
        imdb_name="casting_department", name_en="Casting department", name_ru="Кастинг"
    ),
    PersonProfessionSDM(
        imdb_name="special_effects", name_en="Special effects", name_ru="Спецэффекты"
    ),
    PersonProfessionSDM(
        imdb_name="transportation_department",
        name_en="Transportation department",
        name_ru="Транспорт",
    ),
    PersonProfessionSDM(imdb_name="actress", name_en="Actress", name_ru="Актриса"),
    PersonProfessionSDM(imdb_name="composer", name_en="Composer", name_ru="Композитор"),
    PersonProfessionSDM(
        imdb_name="animation_department",
        name_en="Animation department",
        name_ru="Аниматор",
    ),
    PersonProfessionSDM(imdb_name="legal", name_en="Legal", name_ru="Юрист"),
    PersonProfessionSDM(
        imdb_name="art_director", name_en="Art director", name_ru="Арт-директор"
    ),
    PersonProfessionSDM(
        imdb_name="editorial_department",
        name_en="Editorial department",
        name_ru="Монтаж",
    ),
    PersonProfessionSDM(
        imdb_name="music_department",
        name_en="Music department",
        name_ru="Музыкальный отдел",
    ),
    PersonProfessionSDM(
        imdb_name="writer", name_en="Writer", name_ru="Сценарист", crew=True
    ),
    PersonProfessionSDM(imdb_name="manager", name_en="Manager", name_ru="Менеджер"),
    PersonProfessionSDM(
        imdb_name="visual_effects",
        name_en="Visual effects",
        name_ru="Визуальные эффекты",
    ),
    PersonProfessionSDM(imdb_name="stunts", name_en="Stunts", name_ru="Каскадер"),
    PersonProfessionSDM(
        imdb_name="soundtrack", name_en="Soundtrack", name_ru="Саундтрек"
    ),
    PersonProfessionSDM(
        imdb_name="script_department",
        name_en="Script department",
        name_ru="Отдел сценария",
    ),
    PersonProfessionSDM(
        imdb_name="location_management",
        name_en="Location management",
        name_ru="Менеджер по площадке",
    ),
    PersonProfessionSDM(
        imdb_name="cinematographer",
        name_en="Cinematographer",
        name_ru="Оператор-постановщик",
    ),
    PersonProfessionSDM(
        imdb_name="music_artist", name_en="Music artist", name_ru="Музыкант"
    ),
    PersonProfessionSDM(
        imdb_name="archive_footage",
        name_en="Archive footage",
        name_ru="Специалист по архивным видеозаписям",
    ),
    PersonProfessionSDM(imdb_name="actor", name_en="Actor", name_ru="Актер"),
    PersonProfessionSDM(imdb_name="producer", name_en="Producer", name_ru="Продюсер"),
    PersonProfessionSDM(
        imdb_name="camera_department",
        name_en="Camera department",
        name_ru="Операторская группа",
    ),
    PersonProfessionSDM(
        imdb_name="sound_department",
        name_en="Sound department",
        name_ru="Звукооператор",
    ),
    PersonProfessionSDM(
        imdb_name="publicist", name_en="Publicist", name_ru="Публицист"
    ),
    PersonProfessionSDM(
        imdb_name="assistant_director",
        name_en="Assistant director",
        name_ru="Второй режиссер",
    ),
    PersonProfessionSDM(
        imdb_name="accountant", name_en="Accountant", name_ru="Бухгалтер"
    ),
    PersonProfessionSDM(
        imdb_name="costume_department",
        name_en="Costume department",
        name_ru="Художник по костюмам",
    ),
    PersonProfessionSDM(
        imdb_name="electrical_department",
        name_en="Electrical department",
        name_ru="Электротехник",
    ),
]
