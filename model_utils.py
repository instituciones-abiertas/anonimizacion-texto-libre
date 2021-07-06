import spacy, re
from spacy.tokens import Span
from spacy.language import Language
from utils import bcolors

class Nlp:
	def __init__(self, model_name):
		self.nlp = spacy.load(model_name)
		self.doc = None
		self.nlp.add_pipe("check_misc_and_org", after= "ner")

	def generate_doc(self, text):
		return self.nlp(text)

def get_best_match_for_misc_or_org(ent_to_find_match, all_ents):
	# print(f"\n buscando match de: {ent_to_find_match}")
	#FIXME se puede optimizar de alguna manera? filter?
	results = [ent for ent in all_ents if ent_to_find_match.text in ent.text]
	if len(results):
		print(f"match found for: {ent_to_find_match.text} - results: {results}")
		return results[0]
	return []

@Language.component("check_misc_and_org")
def check_misc_and_org(doc):
	labels_to_check = ["MISC", "ORG"]
	per_and_loc_ents = [ent for ent in doc.ents if ent.label_ in ["PER", "LOC"] and ent.label_ not in labels_to_check]
	l = []
	for old_ent in doc.ents:
		if old_ent.label_ in labels_to_check and len(old_ent.text) > 2:
			matched_ent = get_best_match_for_misc_or_org(old_ent, per_and_loc_ents)
			if matched_ent:
				# print(f"matched_ent: {matched_ent} based on: {old_ent} that used to be: {old_ent.label_}")
				new_ent = Span(doc, old_ent.start, old_ent.end, matched_ent.label_)
				l.append(new_ent)
		else: #removes labels_to_check from doc.ents
			l.append(old_ent)
	l = tuple(l)
	doc.ents = l
	return doc


def replace_tokens_with_labels(doc, color_entities):
	anonymized_text = doc.text
	ents = list(doc.ents)

	for ent in ents:
		print(f"se va a reemplazar ent.text: {ent.text} - {ent.label_}")
		#we replace every ocurrencie no matter it position
		entity_label = f"<{ent.label_}>"
		if color_entities:
			entity_label = bcolors.WARNING+entity_label+bcolors.ENDC
		anonymized_text = anonymized_text.replace(ent.text, f"{entity_label}")

	return anonymized_text


def find_ent_ocurrencies_in_upper_text(text, ents):
	found_texts = []
	upper_pattern= ['[A-ZÀ-ÿ][A-ZÀ-ÿ]+']
	for pattern in upper_pattern:
		match = re.findall(pattern, text)
		ex_cap_text = ' '.join(x.lower() for x in match)
		filtered_ents = list(filter(lambda ent: ent.text.lower() in ex_cap_text, ents))
		for ent in filtered_ents:
			print(f"text: {ent.text} - label: {ent.label_}")
			found_texts.append({"text": ent.text, "entity_name": ent.label_})
	return found_texts


def get_comparison_result(nlp, doc_text, annotations):
	doc = nlp(doc_text)
	ents = doc.ents
	# ver lo que está  hecho en https://recursos.camba.coop/llave-en-mano/ia2/ia2-server/blob/develop/apps/entity/management/commands/stats.py
	return []