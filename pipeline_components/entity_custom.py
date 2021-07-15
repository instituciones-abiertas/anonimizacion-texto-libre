from utils import get_text_from_file
from spacy.tokens import Span
from spacy.util import filter_spans
from spacy.language import Language
from functools import partial


lista_de_enfermedades = get_text_from_file("./data/", "epof.csv", 0, False)
matriculas = get_text_from_file("./data/", "matriculas.csv", 0, False)

# TODO entity custom para:
# dr / dra
# matricula, ver nbors del archivo de matriculas
# enfermedades, ver nbors del archivo de epof

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

address_first_left_nbors = [
    "asentamiento",
    "paraje",
    "country",
    "distrito",
]
address_second_left_nbors = [
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


def is_token_in_x_left_pos(token, pos, nbors):
    try:
        return token.nbor(-pos).lower_ in nbors
    except Exception:
        return False


def is_between_tokens(token_id, left=0, right=0):
    return token_id < right and token_id >= left


is_from_first_tokens = partial(is_between_tokens, left=0, right=3)
is_from_first_2_tokens = partial(is_between_tokens, left=0, right=2)


def get_aditional_left_tokens_for_address(ent):
    if ent.label_ in ["PER"] and ent[-1].nbor().like_num:
        return 1
    if ent.label_ in ["NUM"]:  # FIXME el modelo no detecta NUM
        token = ent[0]
        if token.nbor(-1).lower_ in address_first_left_nbors:
            return 1
        if token.nbor(-2).lower_ in address_first_left_nbors or token.nbor(-2).lower_ in address_second_left_nbors:
            return 2
        if token.nbor(-3).lower_ in address_first_left_nbors:
            return 3
        if token.nbor(-3).lower_ in address_second_left_nbors:
            return 2 - 1 if token.nbor(-2).lower_ == address_connector else 0
        if token.nbor(-4).lower_ in address_first_left_nbors:
            return 4
        if token.nbor(-4).lower_ in address_second_left_nbors:
            return 3 - 1 if token.nbor(-3).lower_ == address_connector else 0
    return 0


def get_aditional_left_tokens_for_drx(ent):
    if ent.label_ in ["PER"]:
        token = ent[0]
        if token.nbor(-1).lower_ in drx_nbor:
            return 1
        if token.nbor(-2).lower_ in drx_nbor:
            return 2
        if token.nbor(-3).lower_ in drx_nbor:
            return 3
        if token.nbor(-4).lower_ in drx_nbor:
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
    ent_start = ent.start - address_token
    ent_to_remove = get_entity_to_remove_if_contained_by(ent_start, ent.end, new_ents)
    if ent_to_remove:
        if (ent.end - ent_start) > (ent_to_remove.end - ent_to_remove.start):
            new_ents = remove_wrong_labeled_entity_span(new_ents, ent_to_remove)
            return Span(doc, ent_start, ent.end, label="DIRECCIÓN")

    return Span(doc, ent_start, ent.end, label="DIRECCIÓN")


def generate_drx_span(ent, new_ents, doc):
    drx_token = get_aditional_left_tokens_for_drx(ent)
    ent_start = ent.start - drx_token
    ent_to_remove = get_entity_to_remove_if_contained_by(ent_start, ent.end, new_ents)
    if ent_to_remove:
        if (ent.end - ent_start) > (ent_to_remove.end - ent_to_remove.start):
            new_ents = remove_wrong_labeled_entity_span(new_ents, ent_to_remove)
            return Span(doc, ent_start, ent.end, label="DRX")

    return Span(doc, ent_start, ent.end, label="DRX")


# TODO revisar!
def is_address(ent):
    first_token = ent[0]
    last_token = ent[-1]
    address_1_tokens_to_left = is_token_in_x_left_pos(first_token, 1, address_first_left_nbors)
    address_2_tokens_to_left_first_nbors = is_token_in_x_left_pos(first_token, 2, address_first_left_nbors)
    address_2_tokens_to_left_second_nbors = is_token_in_x_left_pos(first_token, 2, address_second_left_nbors)
    address_3_tokens_to_left_first_nbors = is_token_in_x_left_pos(first_token, 3, address_first_left_nbors)
    address_3_tokens_to_left_second_nbors = is_token_in_x_left_pos(first_token, 3, address_second_left_nbors)
    address_4_tokens_to_left_first_nbors = is_token_in_x_left_pos(first_token, 4, address_first_left_nbors)
    address_4_tokens_to_left_second_nbors = is_token_in_x_left_pos(first_token, 4, address_second_left_nbors)

    is_address_from_PER = ent.label_ in ["PER"] and (
        address_1_tokens_to_left
        or address_2_tokens_to_left_second_nbors
        or last_token.like_num
        # or (last_token.nbor() and last_token.nbor().like_num) #FIXME por qué busca nbor(1) del ultimo token?
    )

    is_address_from_NUM = ent.label_ in ["NUM"] and (  # FIXME no detecta NUM
        address_1_tokens_to_left
        or address_2_tokens_to_left_first_nbors
        or address_2_tokens_to_left_second_nbors
        or address_3_tokens_to_left_first_nbors
        or address_3_tokens_to_left_second_nbors
        or address_4_tokens_to_left_first_nbors
        or address_4_tokens_to_left_second_nbors
    )

    return is_address_from_PER or is_address_from_NUM


def is_place_token(token):
    # Este enfoque puede generar falsos positivos, tener cuidado con las palabras que se usan
    return (token.nbor(-1).lower_ in address_first_left_nbors and not token.is_stop) or (
        token.nbor(-2).lower_ in address_second_left_nbors
        or token.nbor(-2).lemma_ in address_second_left_nbors
        and not token.is_stop
    )


def is_phone_token(token):
    return token.like_num and (
        token.nbor(-1).lemma_ in phone_lemma
        or token.nbor(-2).lemma_ in phone_lemma
        or token.nbor(-1).text in phone_text
        or token.nbor(-2).text in phone_text
        or (token.nbor(-1).text == "(" and token.nbor(1).text == ")")
    )


def is_phone(ent):
    first_token = ent[0]
    return (
        first_token.nbor(-1).lemma_ in phone_lemma
        or first_token.nbor(-2).lemma_ in phone_lemma
        or first_token.nbor(-3).lemma_ in phone_lemma
        or first_token.nbor(-1).text in phone_text
        or first_token.nbor(-2).text in phone_text
        or (first_token.nbor(-1).text == "(" and first_token.nbor(1).text == ")")
    )


def is_doctor(ent):
    first_token = ent[0]
    return ent.label_ == "PER" and (
        first_token.nbor(-1).text in drx_nbor
        or first_token.nbor(-2).text in drx_nbor
        or first_token.nbor(-3).text in drx_nbor
        or f"{first_token.nbor(-2).text} {first_token.nbor(-1).text}" in drx_nbor_2_tokens
        or f"{first_token.nbor(-3).text} {first_token.nbor(-2).text}" in drx_nbor_2_tokens
    )


@Language.component("entity_custom")
def entity_custom(doc):
    new_ents = []

    def add_span(start, end, label):
        new_ents.append(Span(doc, start, end, label=label))

    for token in doc:
        # print(f"token_ {token}")
        if not is_from_first_2_tokens(token.i) and is_place_token(token):
            add_span(token.i - 1, token.i + 1, "LOC")
        if not is_from_first_tokens(token.i) and is_phone_token(token):
            add_span(token.i - 1, token.i + 1, "NUM_TELÉFONO")

    print(f"\ndoc.ents: {doc.ents}")
    for i, ent in enumerate(doc.ents):
        # print(f"text: {ent.text} - label: {ent.label_}")
        if not is_from_first_tokens(ent.start) and is_address(ent):
            print(f"address  ent: {ent}")
            new_ents.append(generate_address_span(ent, new_ents, doc))
        if not is_from_first_2_tokens(ent.start) and is_phone(ent):
            # TODO entra acá en algún momento???
            print(f"phone  ent: {ent}")
            add_span(ent.start, ent.end, "NUM_TELÉFONO")
        if not is_from_first_2_tokens(ent.start) and is_doctor(ent):
            new_ents.append(generate_drx_span(ent, new_ents, doc))

    if new_ents:
        # We'd always want the new entities to be appended first because
        # filter_spans prioritizes the first occurrences on overlapping
        doc.ents = filter_spans(new_ents + list(doc.ents))

    return doc
