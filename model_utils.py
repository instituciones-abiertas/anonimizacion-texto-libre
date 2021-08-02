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

        self.nlp.add_pipe("check_uppercase_ent", last=True)

    def generate_doc(self, text):
        return self.nlp(text)


def get_best_match_for_misc_or_org(ent_to_find_match, all_ents):
    results = [ent for ent in all_ents if ent_to_find_match.text in ent.text]
    if len(results):
        # print(f"get_best_match_for_misc_or_org - match found for: {ent_to_find_match.text} - results: {results}")
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

    doc.ents = filter_spans(lents + list(doc.ents))
    return doc


@Language.component("check_uppercase_ent")
def check_entities_in_uppercase_text(doc):
    lents = []
    new_uppercase_ents = get_entities_in_uppercase_text(doc, doc.text, doc.ents)
    for uppercase_ent in new_uppercase_ents:
        new_ent = Span(doc, uppercase_ent.start, uppercase_ent.end, uppercase_ent.label_)
        lents.append(new_ent)

    doc.ents = filter_spans(lents + list(doc.ents))
    return doc


def replace_tokens_with_labels(doc, color_entities):
    anonymized_text = doc.text
    ents = list((doc.ents))
    filtered_ents = [ent for ent in ents if ent.label_ not in EXCLUDED_ENTS]
    for ent in filtered_ents:
        # print(f"se va a reemplazar ent.text: {ent.text} - {ent.label_}")
        # we replace every ocurrency no matter it position
        entity_label = f"<{ent.label_}>"
        if color_entities:
            entity_label = bcolors.WARNING + entity_label + bcolors.ENDC
        anonymized_text = anonymized_text.replace(ent.text, f"{entity_label}")

    return anonymized_text


### Auxiliary functions for capitalized text search


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
    upper_pattern = [r"[A-ZÀ-ÿ][A-ZÀ-ÿ]+\.*"]
    for pattern in upper_pattern:
        match = re.findall(pattern, text)
        ex_cap_text = " ".join(x.lower() for x in match)
        filtered_ents = list(filter(lambda ent: ent.text.lower() in ex_cap_text, ents))
        for ent in filtered_ents:
            found_texts.append({"text": ent.text, "entity_name": ent.label_})
    return found_texts


def get_entities_in_uppercase_text(doc, text, ents):
    result = []
    found_texts = find_ent_ocurrencies_in_upper_text(text, ents)
    for element in found_texts:
        found_text, entity_name = element.values()
        for match in re.finditer(found_text, text, flags=re.IGNORECASE):
            new_span = doc.char_span(match.span()[0], match.span()[1], entity_name)
            if new_span and not overlap_ocurrency_list(new_span.start, new_span.end, ents, False):
                result.append(new_span)
    return result


####


def anonymize_text(nlp, text, color_entities):
    doc = nlp.generate_doc(sanitize_text(text))
    anonymized_text = replace_tokens_with_labels(doc, color_entities)
    return anonymized_text


def calculate_total(ents_list):
    c = [ents_list.count(x) for x in ents_list]
    return dict(zip(ents_list, c))


def get_comparison_result(nlp, doc_text, annotations):
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


def sanitize_text(text):
    # cleaning the text to remove extra whitespace
    clean_text = " ".join(text.split())

    # remove marker tickers
    clean_text = re.sub('"', "", clean_text)

    # remove html tags
    clean_text = re.sub(r"<.*?>", " ", clean_text)

    return clean_text
