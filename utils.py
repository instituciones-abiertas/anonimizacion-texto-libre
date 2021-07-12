import os
import sys
import csv
import logging
from collections import defaultdict


logger = logging.getLogger("CIECTI logger")


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# check if dir exist if not create it
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


def are_parameters_ok_to_anonymize(args):
    if not args.file_name and not args.text:
        print("Debes elegir al menos una opción de anonimización: archivo o texto.")
        return False

    if args.file_name and args.text:
        print(
            "Debes elegir una sola opción de anonimización: archivo "
            + bcolors.WARNING
            + "(parámetro '--file_name')"
            + bcolors.ENDC
            + " o texto "
            + bcolors.WARNING
            + "(parámetro '--text')"
            + bcolors.ENDC
            + " ."
        )
        return False

    if args.save_file:
        if not args.destination_folder or not os.path.isdir(args.destination_folder):
            print(
                "No has definido la ubicación de destino "
                + bcolors.WARNING
                + "(falta el parámetro '--destination_folder')"
                + bcolors.ENDC
                + " para el documento anonimizado o la carpeta destino no existe."
            )
            return False

    if args.file_name:
        if not args.origin_path or not os.path.isdir(args.origin_path):
            print(
                "No has definido la ubicación del archivo a anonimizar"
                + bcolors.WARNING
                + "(falta el parámetro '--origin_path')"
                + bcolors.ENDC
                + " o la carpeta origen no existe."
            )
            return False

        if args.column_to_use is None:
            print(
                "No has definido la columna a anonimizar del archivo "
                + bcolors.WARNING
                + "(falta el parámetro '--column_to_use')"
                + bcolors.ENDC
                + "."
            )
            return False

    return True


def get_text_from_file(origin_path, file_name, column_to_use):
    """
    :param origin_path: Path to the file to be used.
    :param file_name: Name of the file that contains the needed text.
    :param column_to_use: Column that contains the text to be used, indicate the column index (consider that the first index is zero).
    :return: Text obtained from the column from the file.
    """
    file_path = origin_path + file_name
    with open(file_path, "r") as file:
        columns = []
        reader = csv.DictReader(file)
        for row in reader:
            if type(column_to_use) == str:
                only_included_cols = dict(filter(lambda elem: elem[0] == column_to_use, row.items()))
            else:
                only_included_cols = dict(filter(lambda elem: elem[column_to_use], row.items()))
            for (k, v) in only_included_cols.items():
                columns.append(v)
        return columns


def save_csv_file(filename, doc, destination_folder):
    name, _ = filename.split(".")
    file_name = name + "_anonimizado.csv"

    with open(destination_folder + "/" + file_name, "w") as file:
        writer = csv.DictWriter(file, fieldnames=["texto_anonimizado"])
        writer.writeheader()
        for text in doc:
            writer.writerow({"texto_anonimizado": text})

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
