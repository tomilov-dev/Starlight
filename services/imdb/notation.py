class TITLE_REGION:
    US = "US"
    RU = "RU"


class NOTATION(object):
    pass


class AKAS(NOTATION):
    TCONST = "titleId"
    ORDERING = "ordering"
    TITLE = "title"
    REGION = "region"
    LANGUAGE = "language"
    TYPES = "types"
    ATTRIBUTES = "attributes"
    IS_ORIGINAL_TITLE = "isOriginalTitle"


class BASICS(NOTATION):
    TCONST = "tconst"
    TITLE_TYPE = "titleType"
    PRIMARY_TITLE = "primaryTitle"
    ORIGINAL_TITLE = "originalTitle"
    IS_ADULT = "isAdult"
    START_YEAR = "startYear"
    END_YEAR = "endYear"
    RUNTIME = "runtimeMinutes"
    GENRES = "genres"


class RATINGS(NOTATION):
    TCONST = "tconst"
    RATE = "averageRating"
    VOTES = "numVotes"

    WRATE = "wrate"
