LOGGER_NAME = "CIECTI logger"
DEFAULT_ANONYMIZED_FILE_NAME = "texto_anonimizado.txt"
DEFAULT_EVALUATE_EFFICIENCY_FILE_NAME = "evaluate_efficiency_results.csv"

# Model
MODEL_NAME = "es_core_news_lg"  # Only detects: LOC, MISC, ORG, PER
EXCLUDED_ENTS = ["MISC", "ORG"]

ENTITIES_LIST = [
    "PER",
    "LOC",
    "DIRECCIÓN",
    "NUM_TELÉFONO",
    "CORREO_ELECTRÓNICO",
    "NUM_DNI",
    "NUM_CUIT_CUIL",
    "PASAPORTE",
    "MATRICULA",
    "EPOF",
    "DRX",
]

# EPOF file
EPOF_FOLDER = "./data/"
EPOF_FILE_NAME = "epof.csv"
EPOF_COLUMN_TO_USE = 0
EPOF_INCLUDE_TITLES = False

# Matriculas file
MATRICULAS_FOLDER = "./data/"
MATRICULAS_FILE_NAME = "matriculas.csv"
MATRICULAS_COLUMN_TO_USE = 0
MATRICULAS_INCLUDE_TITLES = False

# EPOF Phrase Matcher
MATCH_PERCENTAGE = 92  # when finding matches for epof, it will keep matches over this percentage  of matching
