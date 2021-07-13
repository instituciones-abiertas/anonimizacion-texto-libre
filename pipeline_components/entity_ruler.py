from utils import get_text_from_file

lista_de_enfermedades = get_text_from_file("./data/", "epof.csv", 0, False)
matriculas = get_text_from_file("./data/", "matriculas.csv", 0, False)

dni = [
    {"label": "NUM_DNI", "pattern": [{"SHAPE": "d.ddd.ddd"}]},
    {"label": "NUM_DNI", "pattern": [{"SHAPE": "dd.ddd.ddd"}]},
    {"label": "NUM_DNI", "pattern": [{"SHAPE": "ddd.ddd.ddd"}]},
]

# FIXME detecta fijos y celulares? buscar regex porque NO detecta 3517856841

telefonos = [
    {"label": "NUM_TELÉFONO", "pattern": [{"SHAPE": "dddddddddd"}]},
    {"label": "NUM_TELÉFONO", "pattern": [{"SHAPE": "dd-dddd-dddd"}]},
    {"label": "NUM_TELÉFONO", "pattern": [{"SHAPE": "dddd-dddd"}]},
    {"label": "NUM_TELÉFONO", "pattern": [{"SHAPE": "dddd-ddd-dddd"}]},
    {"label": "NUM_TELÉFONO", "pattern": [{"SHAPE": "ddd-ddd-dddd"}]},
]

ruler_patterns = [
    {"label": "CORREO_ELECTRÓNICO", "pattern": [{"LIKE_EMAIL": True}]},
    {"label": "NUM_CUIT_CUIL", "pattern": [{"TEXT": {"REGEX": "^(20|23|27|30|33)([0-9]{9}|-[0-9]{8}-[0-9]{1})$"}}]},
    {"label": "PASAPORTE", "pattern": [{"TEXT": {"REGEX": "^([a-zA-Z]{3}[0-9]{6})$"}}]},
    {
        "label": "MATRICULA",
        "pattern": [{"LOWER": {"IN": matriculas}}, {"ORTH": " ", "OP": "*"}, {"IS_DIGIT": True, "LENGTH": 5}],
    },
    {
        "label": "MATRICULA",
        "pattern": [{"LOWER": {"IN": matriculas}}, {"ORTH": " ", "OP": "*"}, {"IS_DIGIT": True, "LENGTH": 4}],
    },
    {"label": "EPOF", "pattern": [{"ORTH": {"IN": lista_de_enfermedades}}]},
]

ruler_patterns.extend(dni)
ruler_patterns.extend(telefonos)
