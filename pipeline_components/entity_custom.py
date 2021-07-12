from utils import get_text_from_file

lista_de_enfermedades = get_text_from_file("./data/", "epof.csv", 0)
matriculas = get_text_from_file("./data/", "matriculas.csv", 0)


# TODO entity custom para: direccion, teléfono, dr / dra, ciudad / localidad, matricula, analizar NUMs para ver si es teléfono / matrícula
