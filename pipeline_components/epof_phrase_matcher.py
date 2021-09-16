from utils import get_epof
from spacy.language import Language
from phruzz_matcher.phrase_matcher import PhruzzMatcher

lista_de_enfermedades = get_epof()
MATCH_PERCENTAGE = 92


@Language.factory("epof_phrase_matcher")
def epof_phrase_matcher(nlp: Language, name: str):
    return PhruzzMatcher(nlp, lista_de_enfermedades, "EPOF", MATCH_PERCENTAGE)
