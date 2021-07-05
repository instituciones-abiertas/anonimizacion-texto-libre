import os, sys
import argparse
from time import time
from utils import create_logger, check_dir, generate_csv_file, save_doc_file
from model_utils import Nlp, replace_tokens_with_labels, get_comparison_result
from spacy.lang.es.examples import sentences  #FIXME eliminar cuando no se use mas
import random #FIXME eliminar cuando no se use mas

logger = create_logger()

def anonymize_doc(destination_folder=None, text=None, origin_path=None, file_name=False, column_to_use=None):
	"""
	:param origin_path: Path to the file to be anonymized.
	:param destination_folder: Path where the anonymized file is going to be saved.
	:return: Notification when the process is finished.
	"""

	parser = argparse.ArgumentParser()
	parser.add_argument("function", help="To anonymize you should call anonymize_doc", type=str)
	parser.add_argument("--text", help="The text to be anonymized", type=str)
	parser.add_argument("--destination_folder", help="Path where the anonymized file is going to be saved", type=str)
	parser.add_argument("--origin_path", help="Path to the file to be anonymized", type=str)
	parser.add_argument("--file_name", help="The file name to be used", type=str)
	parser.add_argument("--column_to_use", help="Column to use from the file (only one)", type=str)
	args = parser.parse_args()

	can_execute = True
	if not args.file_name and not args.text:
		can_execute = False
		print("Debes elegir al menos una opción de anonimización: archivo o texto.")

	if args.file_name and args.text:
		can_execute = False
		print("Debes elegir una sola opción de anonimización: archivo o texto.")

	if not args.destination_folder or not os.path.isdir(args.destination_folder):
		can_execute = False
		print("No has definido la ubicación de destino para el documento anonimizado o la carpeta destino no existe.")

	if args.file_name:
		if not args.origin_path or not os.path.isdir(args.origin_path):
			can_execute = False
			print(f"No has definido la ubicación del archivo a anonimizar o la carpeta origen no existe.")

		if not args.column_to_use:
			can_execute = False
			print("No has definido la columna a anonimizar del archivo.")

	if can_execute:
		start = time()
		#FIXME revisar el mensaje que se muestra acá
		logger.info(f"""Anonimizando el documento: {args.origin_path}. 
		\nEl documento anonimizado se guardará en la carpeta: {destination_folder}. 
		\nEl archivo anonimizado tendrá el mismo nombre que el archivo original al cual se le agregará '_anonimizado' al final.""")

		#TODO el input va a ser texto libre o archivo csv con una columna que se va a anonimizar
		if args.text:
			doc_text = args.text
			print(f"se anonimiza texto libre => doc_text: {doc_text}")
		else:
			doc_text = sentences[random.randint(0,len(sentences)-1)] #texto de ejemplo
		nlp = Nlp("es_core_news_sm")
		doc = nlp.generate_doc(doc_text)

		anonymized_doc = replace_tokens_with_labels(doc)
		if not args.destination_folder:
			print(f"Texto anonimizado: \n{anonymized_doc}")
		else:
			#FIXME si no hay origin_path, debería generarse un archivo con un nombre por default
			save_doc_file(origin_path, anonymized_doc, destination_folder)

		logger.info(f"Anonimización finalizada en {time() - start} segundos.")
	else:
		dir_path = os.path.dirname(os.path.realpath(__file__))
		#FIXME revisar el mensaje que se muestra acá
		print(f"Si el archivo o la carpeta destino está en la misma ubicación que este script, el path debería comenzar con: {dir_path+'/'}")


def evaluate_efficiency(doc_origin_path=None, json_origin_path=None, destination_folder=None):
	"""
	:param doc_origin_path: Path to the file to be analyzed.
	:param json_origin_path: Path to the document annotations file.
	:param destination_folder: Path where the comparison results file is going to be saved. The file will be called results.csv.
	:return: Notification when the process is finished.
	"""	
	can_execute = True
	if not doc_origin_path:
		can_execute = False
		print(f"No has definido la ubicación del archivo a anonimizar o el archivo no existe.\nAsegúrate de ingresar el path completo.")

	if not json_origin_path:
		can_execute = False
		print(f"No has definido la ubicación del archivo json con las anotaciones del documento a analizar o el archivo no existe.\nAsegúrate de ingresar el path completo.")

	if not destination_folder:
		can_execute = False
		print("No has definido la ubicación de destino para el archivo de resultados del análisis o la carpeta destino no existe.\nAsegúrate de ingresar el path completo.")

	if can_execute:
		start = time()
		logger.info(f"""Analizando el documento: {doc_origin_path} junto al archivo de anotaciones: {json_origin_path}. 
			\nEl resultado del análisis se guardará en la carpeta: {destination_folder}.""")

		nlp = Nlp("es_core_news_sm") 
		doc_text = sentences[random.randint(0,len(sentences)-1)] #texto de ejemplo
		result = get_comparison_result(nlp, doc_text, annotations)
		generate_csv_file(result, destination_folder, logger)
		logger.info(f"Análisis finalizado en {time() - start} segundos.")
		print("Proceso terminado en {time() - start} segundos.")
	else:
		dir_path = os.path.dirname(os.path.realpath(__file__))
		print(f"Si el archivo o la carpeta destino está en la misma ubicación que este script, el path debería comenzar con: {dir_path+'/'}")


if __name__ == "__main__":
	args = sys.argv
	# args[0] = current file
	# args[1] = function name
	# args[2] = function args: (*unpacked)
	globals()[args[1]](*args[2:])