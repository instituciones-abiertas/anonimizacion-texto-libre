import re
from utils import get_epof
from configuration import MATCH_PERCENTAGE
from rapidfuzz import fuzz
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span, Doc
from spacy.util import filter_spans
from spacy.language import Language

lista_de_enfermedades = get_epof()


@Language.factory("epof_phrase_matcher")
def epof_phrase_matcher(nlp: Language, name: str):
    return EpofPhraseMatcher(nlp)


class EpofPhraseMatcher:
    def __init__(self, nlp: Language):
        self.matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        patterns = list(nlp.tokenizer.pipe(lista_de_enfermedades))
        self.matcher.add("epof_list", patterns)

    def __call__(self, doc: Doc) -> Doc:
        matches = self.matcher(doc)

        if matches:
            # using PhraseMatcher from Spacy
            match = matches[0]
            start = match[-2]
            end = match[-1]
        else:
            # using FuzzyWuzzy to find matches
            tokens = [token.text for token in doc]
            match = fuzzy_matcher(lista_de_enfermedades, tokens, MATCH_PERCENTAGE)
            if match:
                start = match[-2]
                end = match[-1] + 1

        if match:
            doc.ents = filter_spans([Span(doc, start, end, label="EPOF")] + list(doc.ents))

        return doc


def fuzzy_matcher(features, tokens, match=None):
    matches = []
    for feature in features:
        feature_length = len(feature.split(" "))
        for i in range(len(tokens) - feature_length + 1):
            matched_phrase = ""
            j = 0
            for j in range(i, i + feature_length):
                if re.search(r"[,!?{}\[\]]", tokens[j]):
                    break
                matched_phrase = matched_phrase + " " + tokens[j].lower()
            matched_phrase.strip()
            if not matched_phrase == "":

                if fuzz.ratio(matched_phrase, feature.lower()) > match:
                    matches.append([matched_phrase, feature, i, j])

    return matches[0] if len(matches) else matches
