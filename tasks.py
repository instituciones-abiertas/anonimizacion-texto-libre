import os, sys
import argparse
from time import time
from utils import bcolors, create_logger, check_dir, generate_csv_file, save_txt_file, are_parameters_ok_to_anonymize, get_text_from_file
from model_utils import Nlp, replace_tokens_with_labels, get_comparison_result

logger = create_logger()
DEFAULT_FILE_NAME = "texto.txt"


def anonymize_doc(text=None, save_file=False, origin_path=None, file_name=False, column_to_use=None, destination_folder=None):
	"""
	:param origin_path: Path to the file to be anonymized.
	:param destination_folder: Path where the anonymized file is going to be saved.
	:return: Notification when the process is finished.
	"""

	parser = argparse.ArgumentParser()
	parser.add_argument("function", help="To anonymize you should call anonymize_doc", type=str)
	parser.add_argument("--text", help="The text to be anonymized", type=str)
	parser.add_argument("--save_file", help="Would you like to save a file or show results in the console?", action="store_true")
	parser.add_argument("--origin_path", help="Path to the file to be anonymized", type=str)
	parser.add_argument("--file_name", help="The filename from the file to be anonymized", type=str)
	parser.add_argument("--column_to_use", help="Column to use from the file (only one), indicate it name", type=str)
	parser.add_argument("--destination_folder", help="Path where the anonymized file is going to be saved", type=str)
	args = parser.parse_args()

	can_execute = are_parameters_ok_to_anonymize(args)

	if can_execute:
		start = time()
		
		if args.text:
			to_anonymize_label = "texto"
			to_anonymize = args.text
		else:
			to_anonymize_label = "archivo"
			to_anonymize = args.file_name

		logger.info(f"""Anonimizando el {to_anonymize_label}: {to_anonymize}. 
			\nEl resultado de la anonimización se guardará en la carpeta: {args.destination_folder}.""")

		#FIXME me quedo con el primer valor del archivo, vamos a permitir multiples filas?
		doc_text = args.text if args.text else get_text_from_file(args.origin_path, args.file_name, args.column_to_use)[0]

		nlp = Nlp("es_core_news_sm")
		doc = nlp.generate_doc(doc_text)
		anonymized_doc = replace_tokens_with_labels(doc)

		if args.save_file:
			save_txt_file(args.file_name or DEFAULT_FILE_NAME, anonymized_doc, args.destination_folder)
		else:
			print(f"Texto anonimizado: \n{anonymized_doc}")

		logger.info(f"Anonimización finalizada en {time() - start} segundos.")
	else:
		print(f"Revise los parámetros enviados para poder anonimizar. Para más información consulte la ayuda: "+bcolors.WARNING +"'python tasks.py anonymize_doc --help'"+bcolors.ENDC +".")


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

		annotations =""
		nlp = Nlp("es_core_news_sm") 
		doc_text = "texto de ejemplo"
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