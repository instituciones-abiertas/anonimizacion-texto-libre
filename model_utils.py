import spacy
import re
from utils import bcolors, ENTITIES_LIST
from spacy.tokens import Span
from spacy.language import Language
from pipeline_components.entity_ruler import ruler_patterns
from pipeline_components.entity_custom import entity_custom
from pipeline_components.epof_phrase_matcher import EpofPhraseMatcher
from collections import Counter

EXCLUDED_ENTS = ["MISC", "ORG"]


class Nlp:
    def __init__(self, model_name):
        self.nlp = spacy.load(model_name)
        self.doc = None

        self.nlp.add_pipe("check_misc_and_org", after="ner")

        ruler = self.nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})
        ruler.add_patterns(ruler_patterns)

        self.nlp.add_pipe("epof_phrase_matcher")
        self.nlp.add_pipe("entity_custom")

    def generate_doc(self, text):
        return self.nlp(text)


def get_best_match_for_misc_or_org(ent_to_find_match, all_ents):
    results = [ent for ent in all_ents if ent_to_find_match.text in ent.text]
    if len(results):
        print(f"get_best_match_for_misc_or_org - match found for: {ent_to_find_match.text} - results: {results}")
        return results[0]
    return []


@Language.component("check_misc_and_org")
def check_misc_and_org(doc):
    labels_to_check = ["MISC", "ORG"]
    per_and_loc_ents = [ent for ent in doc.ents if ent.label_ in ["PER", "LOC"] and ent.label_ not in labels_to_check]
    lents = []
    for old_ent in doc.ents:
        if old_ent.label_ in labels_to_check and len(old_ent.text) > 2:
            matched_ent = get_best_match_for_misc_or_org(old_ent, per_and_loc_ents)
            if matched_ent:
                # print(f"matched_ent: {matched_ent} based on: {old_ent} that used to be: {old_ent.label_}")
                new_ent = Span(doc, old_ent.start, old_ent.end, matched_ent.label_)
                lents.append(new_ent)
        else:  # removes labels_to_check from doc.ents
            lents.append(old_ent)
    lents = tuple(lents)
    doc.ents = lents
    return doc


def replace_tokens_with_labels(doc, color_entities):
    anonymized_text = doc.text
    ents = list(doc.ents)
    filtered_ents = [ent for ent in ents if ent.label_ not in EXCLUDED_ENTS]
    for ent in filtered_ents:
        # print(f"se va a reemplazar ent.text: {ent.text} - {ent.label_}")
        # we replace every ocurrency no matter it position
        entity_label = f"<{ent.label_}>"
        if color_entities:
            entity_label = bcolors.WARNING + entity_label + bcolors.ENDC
        anonymized_text = anonymized_text.replace(ent.text, f"{entity_label}")

    return anonymized_text


# def find_ent_ocurrencies_in_upper_text(text, ents):
#     found_texts = []
#     upper_pattern = ["[A-ZÀ-ÿ][A-ZÀ-ÿ]+"]
#     for pattern in upper_pattern:
#         match = re.findall(pattern, text)
#         ex_cap_text = " ".join(x.lower() for x in match)
#         filtered_ents = list(filter(lambda ent: ent.text.lower() in ex_cap_text, ents))
#         for ent in filtered_ents:
#             found_texts.append({"text": ent.text, "entity_name": ent.label_})
#     return found_texts


def anonymize_text(nlp, text, color_entities):
    doc = nlp.generate_doc(text)
    # FIXME no detecta algunas cosas en mayusculas, agregarlo a la clase NLP?
    # found_texts = find_ent_ocurrencies_in_upper_text(doc.text, doc.ents)

    anonymized_text = replace_tokens_with_labels(doc, color_entities)
    return anonymized_text


def calculate_total(ents_list):
    c = [ents_list.count(x) for x in ents_list]
    return dict(zip(ents_list, c))


def get_comparison_result(nlp, doc_text, annotations):
    # FIXME seria bueno usar anonymize_text porque considera las mayúsculas
    results = []
    ents = nlp.generate_doc(doc_text).ents

    ents_list = [ent.label_ for ent in ents]
    ents_totals = calculate_total(ents_list)

    ents_list = [annot["entity"] for annot in annotations]
    annotations_totals = calculate_total(ents_list)

    for ent in ENTITIES_LIST:
        ent_total = ents_totals.get(ent) if ents_totals.get(ent) else 0
        annotation_total = annotations_totals.get(ent) if annotations_totals.get(ent) else 0
        if ent_total and annotation_total:
            efficiency = ent_total / annotation_total * 100
        else:
            efficiency = 100 if ent_total > annotation_total else 0

        results.append(
            {
                "entity": ent,
                "model": ent_total,
                "expected": annotation_total,
                "efficiency": efficiency,
            }
        )
    return results
