import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))
from services.models import PersonProfessionServiceDM


professions: list[PersonProfessionServiceDM] = [
    PersonProfessionServiceDM(imdb_name="self", name_en="Self", name_ru="В роли себя"),
    PersonProfessionServiceDM(imdb_name="editor", name_en="Editor", name_ru="Монтажер"),
    PersonProfessionServiceDM(
        imdb_name="miscellaneous", name_en="Miscellaneous", name_ru="Различные работы"
    ),
    PersonProfessionServiceDM(
        imdb_name="choreographer", name_en="Choreographer", name_ru="Хореограф"
    ),
    PersonProfessionServiceDM(
        imdb_name="director", name_en="Director", name_ru="Режиссер", crew=True
    ),
    PersonProfessionServiceDM(
        imdb_name="set_decorator", name_en="Set decorator", name_ru="Декоратор"
    ),
    PersonProfessionServiceDM(
        imdb_name="assistant", name_en="Assistant", name_ru="Ассистент"
    ),
    PersonProfessionServiceDM(
        imdb_name="archive_sound",
        name_en="Archive sound",
        name_ru="Специалист по архивным звукозаписям",
    ),
    PersonProfessionServiceDM(
        imdb_name="casting_director",
        name_en="Casting director",
        name_ru="Кастинг-директор",
    ),
    PersonProfessionServiceDM(
        imdb_name="talent_agent",
        name_en="Talent agent",
        name_ru="Агент по поиску талантов",
    ),
    PersonProfessionServiceDM(
        imdb_name="production_manager",
        name_en="Production manager",
        name_ru="Руководитель производства",
    ),
    PersonProfessionServiceDM(
        imdb_name="production_designer",
        name_en="Production designer",
        name_ru="Художник-постановщик",
    ),
    PersonProfessionServiceDM(
        imdb_name="art_department",
        name_en="Art department",
        name_ru="Художественное оформление",
    ),
    PersonProfessionServiceDM(
        imdb_name="podcaster", name_en="Podcaster", name_ru="Подкастер"
    ),
    PersonProfessionServiceDM(
        imdb_name="production_department",
        name_en="Production department",
        name_ru="Производство",
    ),
    PersonProfessionServiceDM(
        imdb_name="make_up_department",
        name_en="Make Up department",
        name_ru="Художник-гример",
    ),
    PersonProfessionServiceDM(
        imdb_name="executive", name_en="Executive", name_ru="Генеральный продюсер"
    ),
    PersonProfessionServiceDM(
        imdb_name="costume_designer",
        name_en="Costume designer",
        name_ru="Художник по костюмам",
    ),
    PersonProfessionServiceDM(
        imdb_name="casting_department", name_en="Casting department", name_ru="Кастинг"
    ),
    PersonProfessionServiceDM(
        imdb_name="special_effects", name_en="Special effects", name_ru="Спецэффекты"
    ),
    PersonProfessionServiceDM(
        imdb_name="transportation_department",
        name_en="Transportation department",
        name_ru="Транспорт",
    ),
    PersonProfessionServiceDM(
        imdb_name="actress", name_en="Actress", name_ru="Актриса"
    ),
    PersonProfessionServiceDM(
        imdb_name="composer", name_en="Composer", name_ru="Композитор"
    ),
    PersonProfessionServiceDM(
        imdb_name="animation_department",
        name_en="Animation department",
        name_ru="Аниматор",
    ),
    PersonProfessionServiceDM(imdb_name="legal", name_en="Legal", name_ru="Юрист"),
    PersonProfessionServiceDM(
        imdb_name="art_director", name_en="Art director", name_ru="Арт-директор"
    ),
    PersonProfessionServiceDM(
        imdb_name="editorial_department",
        name_en="Editorial department",
        name_ru="Монтаж",
    ),
    PersonProfessionServiceDM(
        imdb_name="music_department",
        name_en="Music department",
        name_ru="Музыкальный отдел",
    ),
    PersonProfessionServiceDM(
        imdb_name="writer", name_en="Writer", name_ru="Сценарист", crew=True
    ),
    PersonProfessionServiceDM(
        imdb_name="manager", name_en="Manager", name_ru="Менеджер"
    ),
    PersonProfessionServiceDM(
        imdb_name="visual_effects",
        name_en="Visual effects",
        name_ru="Визуальные эффекты",
    ),
    PersonProfessionServiceDM(imdb_name="stunts", name_en="Stunts", name_ru="Каскадер"),
    PersonProfessionServiceDM(
        imdb_name="soundtrack", name_en="Soundtrack", name_ru="Саундтрек"
    ),
    PersonProfessionServiceDM(
        imdb_name="script_department",
        name_en="Script department",
        name_ru="Отдел сценария",
    ),
    PersonProfessionServiceDM(
        imdb_name="location_management",
        name_en="Location management",
        name_ru="Менеджер по площадке",
    ),
    PersonProfessionServiceDM(
        imdb_name="cinematographer",
        name_en="Cinematographer",
        name_ru="Оператор-постановщик",
    ),
    PersonProfessionServiceDM(
        imdb_name="music_artist", name_en="Music artist", name_ru="Музыкант"
    ),
    PersonProfessionServiceDM(
        imdb_name="archive_footage",
        name_en="Archive footage",
        name_ru="Специалист по архивным видеозаписям",
    ),
    PersonProfessionServiceDM(imdb_name="actor", name_en="Actor", name_ru="Актер"),
    PersonProfessionServiceDM(
        imdb_name="producer", name_en="Producer", name_ru="Продюсер"
    ),
    PersonProfessionServiceDM(
        imdb_name="camera_department",
        name_en="Camera department",
        name_ru="Операторская группа",
    ),
    PersonProfessionServiceDM(
        imdb_name="sound_department",
        name_en="Sound department",
        name_ru="Звукооператор",
    ),
    PersonProfessionServiceDM(
        imdb_name="publicist", name_en="Publicist", name_ru="Публицист"
    ),
    PersonProfessionServiceDM(
        imdb_name="assistant_director",
        name_en="Assistant director",
        name_ru="Второй режиссер",
    ),
    PersonProfessionServiceDM(
        imdb_name="accountant", name_en="Accountant", name_ru="Бухгалтер"
    ),
    PersonProfessionServiceDM(
        imdb_name="costume_department",
        name_en="Costume department",
        name_ru="Художник по костюмам",
    ),
    PersonProfessionServiceDM(
        imdb_name="electrical_department",
        name_en="Electrical department",
        name_ru="Электротехник",
    ),
]
