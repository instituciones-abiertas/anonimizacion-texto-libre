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
	#TODO reemplazar tokens del final hacia el principio (para que no me cambie los indices)
	#ver reemplazo_asincronico_en_texto() en entity/tasks.py
	return text


def get_comparison_result(nlp, doc_text, annotations):
	doc = nlp(doc_text)
	ents = doc.ents
	# ver lo que está  hecho en https://recursos.camba.coop/llave-en-mano/ia2/ia2-server/blob/develop/apps/entity/management/commands/stats.py
	return []