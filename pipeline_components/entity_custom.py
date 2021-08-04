from utils import get_epof, get_matriculas_nbors
from spacy.tokens import Span
from spacy.util import filter_spans
from spacy.language import Language
from functools import partial


lista_de_enfermedades = get_epof()
matriculas = get_matriculas_nbors()

address_first_left_nbors = [
    "calle",
    "Calle",
    "dirección",
    "Dirección",
    "avenida",
    "av.",
    "Avenida",
    "Av.",
    "pasaje",
    "Pasaje",
    "Parcela",
    "parcela",
    "domicilio",
    "casa",
    "Casa",
]

address_second_left_nbors = [
    "instalación",
    "contramano",
    "sita",
    "sitas",
    "sito",
    "sitos",
    "real",
    "domiciliado",
    "domiciliada",
    "constituido",
    "constituida",
    "contramano",
    "intersección",
    "domicilio",
    "ubicado",
    "registrado",
    "ubicada",
    "real",
]

address_connector = "en"

place_first_left_nbors = [
    "asentamiento",
    "paraje",
    "country",
    "distrito",
    "barrio",
]

place_second_left_nbors = [
    "localidad",
    "ciudad",
    "vivir",
    "habitar",
]

phone_lemma = ["teléfono", "tel", "celular", "número", "numerar", "telefónico"]
phone_text = ["telefono", "tel", "cel"]

drx_nbor = [
    "dr",
    "dr.",
    "dra",
    "dra.",
    "doctor",
    "doctora",
    "médico",
    "medico",
    "médica",
    "medica",
]

drx_nbor_2_tokens = [
    "agente sanitario",
    "agente sanitaria",
]


def remove_wrong_labeled_entity_span(ent_list, ent_to_remove):
    return [ent for ent in ent_list if not (ent_to_remove.start == ent.start and ent_to_remove.end == ent.end)]


def is_token_in_x_left_lowers(token, pos, in_list):
    try:
        return token.nbor(pos).lower_ in in_list
    except Exception:
        return False


def is_token_in_x_left_lemma(token, pos, in_list):
    try:
        return token.nbor(pos).lemma_ in in_list
    except Exception:
        return False


def is_token_in_x_left_text(token, pos, in_list):
    try:
        return token.nbor(pos).text in in_list
    except Exception:
        return False


def are_2_tokens_in_x_left_lowers(token, pos_1, pos_2, in_list):
    try:
        return f"{token.nbor(pos_1).lower_} {token.nbor(pos_2).lower_}" in in_list
    except Exception:
        return False


def is_between_tokens(token_id, left=0, right=0):
    return token_id < right and token_id >= left


def get_aditional_left_tokens_for_address(ent):
    if ent.label_ in ["PER"] and ent[-1].nbor().like_num:
        return 1
    if ent.label_ in ["LOC"]:
        token = ent[0]
        if is_token_in_x_left_lowers(token, -1, address_first_left_nbors):
            return 1
        if is_token_in_x_left_lowers(token, -2, address_first_left_nbors) or is_token_in_x_left_lowers(
            token, -2, address_second_left_nbors
        ):
            return 2
        if is_token_in_x_left_lowers(token, -3, address_first_left_nbors):
            return 3
        if is_token_in_x_left_lowers(token, -3, address_second_left_nbors):
            return 2 - 1 if token.nbor(-2).lower_ == address_connector else 0
        if is_token_in_x_left_lowers(token, -4, address_first_left_nbors):
            return 4
        if is_token_in_x_left_lowers(token, -4, address_second_left_nbors):
            return 3 - 1 if token.nbor(-3).lower_ == address_connector else 0
    return 0


def get_aditional_right_tokens_for_address(ent):
    last_ent_pos = ent[len(ent.text.split()) - 1]
    if last_ent_pos.nbor(2).like_num:
        return 2
    if last_ent_pos.nbor(1).like_num:
        return 1
    return 0


def get_aditional_left_tokens_for_address_token(token):
    if is_token_in_x_left_lowers(token, -1, address_first_left_nbors):
        return 1
    if is_token_in_x_left_lowers(token, -2, address_first_left_nbors) or is_token_in_x_left_lowers(
        token, -2, address_second_left_nbors
    ):
        return 2

    if is_token_in_x_left_lowers(token, -3, address_first_left_nbors):
        return 3
    if is_token_in_x_left_lowers(token, -3, address_second_left_nbors) or is_token_in_x_left_lemma(
        token, -3, place_second_left_nbors
    ):
        return 2 - 1 if token.nbor(-2).lower_ == address_connector else 0

    if is_token_in_x_left_lowers(token, -4, address_first_left_nbors):
        return 4
    if is_token_in_x_left_lowers(token, -4, address_second_left_nbors) or is_token_in_x_left_lemma(
        token, -4, place_second_left_nbors
    ):
        return 3 - 1 if token.nbor(-3).lower_ == address_connector else 0
    return 0


def get_aditional_left_tokens_for_drx(token):
    if is_token_in_x_left_lowers(token, -1, drx_nbor):
        return 1
    if is_token_in_x_left_lowers(token, -2, drx_nbor):
        return 2
    if is_token_in_x_left_lowers(token, -3, drx_nbor):
        return 3
    if is_token_in_x_left_lowers(token, -4, drx_nbor):
        return 4
    return 0


def get_entity_to_remove_if_contained_by(ent_start, ent_end, list_entities):
    for i, ent_from_list in enumerate(list_entities):
        if (
            ent_start >= ent_from_list.start
            and ent_start <= ent_from_list.end
            or ent_end >= ent_from_list.start
            and ent_end <= ent_from_list.end
        ):
            return ent_from_list
    return None


def generate_address_span(ent, new_ents, doc):
    address_token = get_aditional_left_tokens_for_address(ent)
    extra_tokens_to_right = get_aditional_right_tokens_for_address(ent)
    ent_start = ent.start - address_token
    ent_end = ent.end + extra_tokens_to_right
    ent_to_remove = get_entity_to_remove_if_contained_by(ent_start, ent_end, new_ents)
    if ent_to_remove:
        if (ent.end - ent_start) > (ent_to_remove.end - ent_to_remove.start):
            new_ents = remove_wrong_labeled_entity_span(new_ents, ent_to_remove)
            return Span(doc, ent_start, ent.end, label="DIRECCIÓN")

    return Span(doc, ent_start, ent_end, label="DIRECCIÓN")


def generate_drx_span(ent, new_ents, doc):
    drx_token = get_aditional_left_tokens_for_drx(ent[0])
    ent_start = ent.start - drx_token
    ent_to_remove = get_entity_to_remove_if_contained_by(ent_start, ent.end, new_ents)
    if ent_to_remove:
        if (ent.end - ent_start) > (ent_to_remove.end - ent_to_remove.start):
            new_ents = remove_wrong_labeled_entity_span(new_ents, ent_to_remove)
            return Span(doc, ent_start, ent.end, label="DRX")

    return Span(doc, ent_start, ent.end, label="DRX")


def is_address(ent):
    first_token = ent[0]
    last_token = ent[-1]
    address_1_tokens_to_left = is_token_in_x_left_lowers(first_token, -1, address_first_left_nbors)
    address_2_tokens_to_left_first_nbors = is_token_in_x_left_lowers(first_token, -2, address_first_left_nbors)
    address_2_tokens_to_left_second_nbors = is_token_in_x_left_lowers(first_token, -2, address_second_left_nbors)
    address_3_tokens_to_left_first_nbors = is_token_in_x_left_lowers(first_token, -3, address_first_left_nbors)
    address_3_tokens_to_left_second_nbors = is_token_in_x_left_lowers(first_token, -3, address_second_left_nbors)
    address_4_tokens_to_left_first_nbors = is_token_in_x_left_lowers(first_token, -4, address_first_left_nbors)
    address_4_tokens_to_left_second_nbors = is_token_in_x_left_lowers(first_token, -4, address_second_left_nbors)

    is_address_from_PER = ent.label_ in ["PER"] and (
        address_1_tokens_to_left or address_2_tokens_to_left_second_nbors or last_token.like_num
    )

    is_address_from_LOC = ent.label_ in ["LOC"] and (
        address_1_tokens_to_left
        or address_2_tokens_to_left_first_nbors
        or address_2_tokens_to_left_second_nbors
        or address_3_tokens_to_left_first_nbors
        or address_3_tokens_to_left_second_nbors
        or address_4_tokens_to_left_first_nbors
        or address_4_tokens_to_left_second_nbors
    )

    return is_address_from_PER or is_address_from_LOC


def is_address_token_from_number(token):
    if token.like_num:
        address_1_tokens_to_left = is_token_in_x_left_lowers(token, -1, address_first_left_nbors)
        address_2_tokens_to_left_first_nbors = is_token_in_x_left_lowers(token, -2, address_first_left_nbors)
        address_2_tokens_to_left_second_nbors = is_token_in_x_left_lowers(token, -2, address_second_left_nbors)
        address_3_tokens_to_left_first_nbors = is_token_in_x_left_lowers(token, -3, address_first_left_nbors)
        address_3_tokens_to_left_second_nbors = is_token_in_x_left_lowers(token, -3, address_second_left_nbors)
        address_4_tokens_to_left_first_nbors = is_token_in_x_left_lowers(token, -4, address_first_left_nbors)
        address_4_tokens_to_left_second_nbors = is_token_in_x_left_lowers(token, -4, address_second_left_nbors)
        address_3_tokens_to_left_lemma = is_token_in_x_left_lemma(token, -3, place_second_left_nbors)
        address_4_tokens_to_left_lemma = is_token_in_x_left_lemma(token, -4, place_second_left_nbors)

        return (
            address_1_tokens_to_left
            or address_2_tokens_to_left_first_nbors
            or address_2_tokens_to_left_second_nbors
            or address_3_tokens_to_left_first_nbors
            or address_3_tokens_to_left_second_nbors
            or address_3_tokens_to_left_lemma
            or address_4_tokens_to_left_first_nbors
            or address_4_tokens_to_left_second_nbors
            or address_4_tokens_to_left_lemma
        )


def is_place_token(token):
    # This approach can generate false positives, be careful with the words used.
    return token.is_title and (
        (is_token_in_x_left_lowers(token, -1, place_first_left_nbors) and not token.is_stop)
        or (
            is_token_in_x_left_lowers(token, -2, address_second_left_nbors)
            or is_token_in_x_left_lemma(token, -2, place_second_left_nbors)
            and not token.is_stop
        )
    )


def is_phone_token(token):
    try:
        has_parenthesis_around = token.nbor(-1).text == "(" and token.nbor(1).text == ")"
    except Exception:
        has_parenthesis_around = False

    return token.like_num and (
        is_token_in_x_left_lemma(token, -1, phone_lemma)
        or is_token_in_x_left_lemma(token, -2, phone_lemma)
        or is_token_in_x_left_text(token, -1, phone_text)
        or is_token_in_x_left_text(token, -2, phone_text)
        or has_parenthesis_around
    )


def is_doctor(ent):
    first_token = ent[0]
    return (ent.label_ == "PER" or ent.label_ == "LOC") and (
        is_token_in_x_left_lowers(first_token, -1, drx_nbor)
        or is_token_in_x_left_lowers(first_token, -2, drx_nbor)
        or is_token_in_x_left_lowers(first_token, -3, drx_nbor)
        or are_2_tokens_in_x_left_lowers(first_token, -2, -1, drx_nbor_2_tokens)
        or are_2_tokens_in_x_left_lowers(first_token, -3, -2, drx_nbor_2_tokens)
    )


def is_doctor_token(token):
    second_nbor_left_is_drx = is_token_in_x_left_lowers(token, -2, drx_nbor)
    second_nbors_left_is_drx = are_2_tokens_in_x_left_lowers(token, -2, -1, drx_nbor_2_tokens)
    third_nbors_left_is_drx = are_2_tokens_in_x_left_lowers(token, -3, -2, drx_nbor_2_tokens)

    return token.is_title and (
        is_token_in_x_left_lowers(token, -1, drx_nbor)
        or second_nbor_left_is_drx
        or second_nbors_left_is_drx
        or third_nbors_left_is_drx
    )


def is_matricula(token):
    splitted_token = token.text.split(".")
    any_part_is_matricula = False
    if token.like_num or splitted_token[0] != token.text:
        any_part_is_matricula = any([part for part in splitted_token if part.lower() in matriculas])

    return (
        token.like_num
        and (
            is_token_in_x_left_lowers(token, -1, matriculas)
            or is_token_in_x_left_lowers(token, -2, matriculas)
            or is_token_in_x_left_lowers(token, -3, matriculas)
        )
        or any_part_is_matricula
    )


@Language.component("entity_custom")
def entity_custom(doc):
    new_ents = []

    def add_span(start, end, label):
        new_ents.append(Span(doc, start, end, label=label))

    for token in doc:
        # print(f"token_ {token}")
        if is_place_token(token):
            add_span(token.i - 1, token.i + 1, "LOC")
        if is_phone_token(token):
            add_span(token.i - 1, token.i + 1, "NUM_TELÉFONO")
        if is_doctor_token(token):
            left_extra_tokens = get_aditional_left_tokens_for_drx(token)
            add_span(token.i - left_extra_tokens, token.i + 1, "DRX")
        if is_address_token_from_number(token):
            left_extra_tokens = get_aditional_left_tokens_for_address_token(token)
            add_span(token.i - left_extra_tokens, token.i + 1, "DIRECCION")
        if is_matricula(token):
            add_span(token.i - 1, token.i + 1, "MATRICULA")

    # print(f"\ndoc.ents: {doc.ents}")
    for i, ent in enumerate(doc.ents):
        # print(f"text: {ent.text} - label: {ent.label_}")
        if is_address(ent):
            new_ents.append(generate_address_span(ent, new_ents, doc))
        if is_doctor(ent):
            new_ents.append(generate_drx_span(ent, new_ents, doc))

    if new_ents:
        # We'd always want the new entities to be appended first because
        # filter_spans prioritizes the first occurrences on overlapping
        doc.ents = filter_spans(new_ents + list(doc.ents))

    return doc
