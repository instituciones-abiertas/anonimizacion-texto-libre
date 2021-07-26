import spacy
from spacy.util import filter_spans
import re
from utils import bcolors
from spacy.tokens import Span
from spacy.language import Language
from pipeline_components.entity_ruler import ruler_patterns
from pipeline_components.entity_custom import entity_custom
from pipeline_components.epof_phrase_matcher import EpofPhraseMatcher
from configuration import EXCLUDED_ENTS, ENTITIES_LIST
import collections


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


def replace_tokens_with_labels(doc, color_entities, uppercase_ents):
    anonymized_text = doc.text
    if uppercase_ents:
        doc.ents = doc.ents.extend(filter_spans(uppercase_ents))
    print(doc.ents)
    ents = list(format_spans(doc.ents))
    print(ents)
    filtered_ents = [ent for ent in ents if ent.label_ not in EXCLUDED_ENTS]
    for ent in filtered_ents:
        # print(f"se va a reemplazar ent.text: {ent.text} - {ent.label_}")
        # we replace every ocurrency no matter it position
        entity_label = f"<{ent.label_}>"
        if color_entities:
            entity_label = bcolors.WARNING + entity_label + bcolors.ENDC
        anonymized_text = anonymized_text.replace(ent.text, f"{entity_label}")

    return anonymized_text


## Funciones para la busqueda de entidades en mayusculas


def format_span(span):
    new_ordered_dict = collections.OrderedDict()
    new_ordered_dict["start"] = span.start_char
    new_ordered_dict["end"] = span.end_char
    new_ordered_dict["tag"] = span.label_
    return new_ordered_dict


def format_spans(span_list):
    # retorna una lista de OrderedDict
    return list(map(format_span, span_list))


def overlap_ocurrency(ent_start, ent_end, ocurrency, use_index):
    ocurrency_start = ocurrency.startIndex if use_index else ocurrency.start
    ocurrency_end = ocurrency.endIndex if use_index else ocurrency.end
    return (
        (ent_start >= ocurrency_start and ent_end <= ocurrency_end)
        or (ent_start <= ocurrency_end and ent_end >= ocurrency_end)
        or (ent_start >= ocurrency_start)
        and (ent_end <= ocurrency_end)
    )


def overlap_ocurrency_list(ent_start, ent_end, original_ocurrency_list, use_index=True):
    return any(overlap_ocurrency(ent_start, ent_end, ocurrency, use_index) for ocurrency in original_ocurrency_list)


def find_ent_ocurrencies_in_upper_text(text, ents):
    found_texts = []
    upper_pattern = ["[A-ZÀ-ÿ][A-ZÀ-ÿ]+"]
    for pattern in upper_pattern:
        match = re.findall(pattern, text)
        ex_cap_text = " ".join(x.lower() for x in match)
        filtered_ents = list(filter(lambda ent: ent.text.lower() in ex_cap_text, ents))
        for ent in filtered_ents:
            found_texts.append({"text": ent.text, "entity_name": ent.label_})
    print(f"Encontre entidades en la mayusculas{found_texts}")
    return found_texts


def get_entities_in_uppercase_text(doc, text, ents):
    result = []
    found_texts = find_ent_ocurrencies_in_upper_text(text, ents)
    for element in found_texts:
        found_text, entity_name = element.values()
        for match in re.finditer(found_text, text):
            print(f"El match {match}")
            new_span = doc.char_span(match.span()[0], match.span()[1], entity_name)
            if new_span and not overlap_ocurrency_list(new_span.start, new_span.end, ents, False):
                result.append(new_span)
    print(f"El resultado es {result}")
    print(f"El resultado es  de tipo{type(result)}")
    return result


def anonymize_text(nlp, text, color_entities):
    doc = nlp.generate_doc(text)
    # FIXME no detecta algunas cosas en mayusculas, agregarlo a la clase NLP?
    uppercase_ents = get_entities_in_uppercase_text(doc, doc.text, doc.ents)
    anonymized_text = replace_tokens_with_labels(doc, color_entities, uppercase_ents)
    return anonymized_text


def calculate_total(ents_list):
    c = [ents_list.count(x) for x in ents_list]
    return dict(zip(ents_list, c))


def get_comparison_result(nlp, doc_text, annotations):
    # FIXME seria bueno usar anonymize_text porque considera las mayúsculas
    results = []
    doc = nlp.generate_doc(doc_text)
    ents = doc.ents

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
