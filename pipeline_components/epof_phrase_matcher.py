from utils import get_text_from_file
from rapidfuzz import process
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
        # FIXME si el texto escrito no coincide 100% con lo de la lista_de_enfermedades => no hay matches
        # ver https://github.com/jackmen/PhuzzyMatcher/blob/master/notebooks/fuzzy_phrase_matcher.ipynb
        matches = self.matcher(doc)

        new_ents = []
        for match_id, start, end in matches:
            print("Matched based on lowercase token text:", doc[start:end])
            # extracted = process.extract(doc[start:end].text, lista_de_enfermedades)
            # print(f"all: {extracted}")
            # one_extracted = process.extractOne(doc[start:end].text, lista_de_enfermedades)
            # print(f"one: {one_extracted}")
            new_ents.append(Span(doc, start, end, label="EPOF"))

        if new_ents:
            doc.ents = filter_spans(new_ents + list(doc.ents))

        return doc
