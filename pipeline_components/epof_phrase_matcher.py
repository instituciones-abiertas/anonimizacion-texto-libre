import re
from utils import get_text_from_file
from rapidfuzz import process, fuzz
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span, Doc
from spacy.util import filter_spans
from spacy.language import Language

lista_de_enfermedades = get_text_from_file("./data/", "epof.csv", 0, False)


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
        new_ents = []

        print(f"matches: {matches}")
        # TODO qué pasa cuando no encuentra nada?

        if len(matches):
            match = matches[0]
            print("Matched based on lowercase token text:", match[0], doc[match[-2] : match[-1]])
            new_ents.append(Span(doc, match[-2], match[-1], label="EPOF"))
        else:
            tokens = [token.text for token in doc]
            match = fuzzy_matcher(lista_de_enfermedades, tokens, 92)
            print("Matched based on lowercase token text:", match[0], doc[match[-2] : match[-1] + 1])
            new_ents.append(Span(doc, match[-2], match[-1] + 1, label="EPOF"))

            # for match_id, epof, start, end in matches:
            #   print("Matched based on lowercase token text:", doc[start:end+1])
            #   new_ents.append(Span(doc, start, end+1, label="EPOF"))

        if new_ents:
            doc.ents = filter_spans(new_ents + list(doc.ents))

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

    return matches[0]
