import os, sys
import csv
import logging

logger = logging.getLogger("CIECTI logger")

#check if dir exist if not create it
def check_dir(file_name):
	directory = os.path.dirname(file_name)
	if not os.path.exists(directory):
		os.makedirs(directory)


def create_logger():
	logger = logging.getLogger("CIECTI logger")
	logger.setLevel(logging.DEBUG)
	log_path = "logs/debug.log"
	check_dir(log_path)
	logger_fh = logging.FileHandler(log_path)
	logger_fh.setLevel(logging.DEBUG)
	formatter = logging.Formatter("[%(asctime)s] (%(name)s) :: %(levelname)s :: %(message)s")
	logger_fh.setFormatter(formatter)
	logger.addHandler(logger_fh)
	return logger


def save_doc_file(origin_path, doc, destination_folder):
	#TODO deben definir el output que necesitan
	name, extension = origin_path.split("/")[-1:][0].split(".")
	file_name = name+"_anonymized."+extension
	with open(file_name, 'w') as file:
		file.write(doc)
		logger.info(f"Se guardó el archivo {file_name} en la carpeta {destination_folder}")


def generate_csv_file(result, destination_folder, logger):
	dir_path = os.path.dirname(os.path.realpath(__file__))
	path = f"{dir_path}/{destination_folder}/results.csv"
	check_dir(path)
	logger.info("\n\n")
	logger.info(f"💾 Guardando resultados de análisis en {path}")
	# create file if not exists
	if not os.path.exists(path):
		with open(path, "w"):
			pass

	header = [
			"Entidad",
			"Modelo",
			"Esperado",
			"Efectividad",
	]
	rows = []
	for item in result:
		rows.append(
			{
					"entity": item.entity,
					"model": item.model,
					"expected": item.expected,
					"efficiency": item.efficiency,
			}
		)

	# opening the csv file in 'w' mode
	file = open(path, "w", newline="")
	with file:
		writer = csv.DictWriter(file, fieldnames=header)
		writer.writeheader()
		for r in rows:
			writer.writerow(r)
