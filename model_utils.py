import spacy

class Nlp:
	def __init__(self, model_name):
		self.nlp = spacy.load(model_name)
		self.doc = None

	def generate_doc(self, text):
		return self.nlp(text)


def replace_tokens_with_labels(doc):
	text = doc.text
	ents = doc.ents
	result = ""
	return result


def get_comparison_result(doc_origin_path, json_origin_path):
	# ver lo que está  hecho en https://recursos.camba.coop/llave-en-mano/ia2/ia2-server/blob/develop/apps/entity/management/commands/stats.py
	return []