import os
import sys
import csv
import logging
from collections import defaultdict
from configuration import (
    LOGGER_NAME,
    EPOF_FOLDER,
    EPOF_FILE_NAME,
    EPOF_COLUMN_TO_USE,
    EPOF_INCLUDE_TITLES,
    MATRICULAS_FOLDER,
    MATRICULAS_FILE_NAME,
    MATRICULAS_COLUMN_TO_USE,
    MATRICULAS_INCLUDE_TITLES,
    DEFAULT_EVALUATE_EFFICIENCY_FILE_NAME,
    ENTITIES_LIST,
)

logger = logging.getLogger(LOGGER_NAME)


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
    logger = logging.getLogger(LOGGER_NAME)
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


def are_parameters_ok_to_evaluate_efficiency(args):
    if not args.origin_path or not os.path.isdir(args.origin_path):
        print(
            "No has definido la ubicación del archivo a utilizar para evaluar la eficiencia del modelo"
            + bcolors.WARNING
            + "(falta el parámetro '--origin_path')"
            + bcolors.ENDC
            + " o la carpeta origen no existe."
        )
        return False

    if not args.file_name:
        print(
            "No has definido el nombre del archivo a utilizar para evaluar la eficiencia del modelo"
            + bcolors.WARNING
            + "(falta el parámetro '--file_name')"
            + bcolors.ENDC
        )
        return False

    if not args.json_origin_path or not os.path.isdir(args.json_origin_path):
        print(
            "No has definido la ubicación del archivo json con las anotaciones a utilizar para evaluar la eficiencia del modelo"
            + bcolors.WARNING
            + "(falta el parámetro '--json_origin_path')"
            + bcolors.ENDC
            + " o la carpeta origen no existe."
        )
        return False

    if not args.json_file_name or "json" not in args.json_file_name:
        print(
            "No has definido el nombre del archivo json con las anotaciones a utilizar para evaluar la eficiencia del modelo o NO es un archivo json"
            + bcolors.WARNING
            + "(falta el parámetro '--json_file_name')"
            + bcolors.ENDC
        )
        return False

    if not args.destination_folder or not os.path.isdir(args.destination_folder):
        print(
            "No has definido la ubicación de destino "
            + bcolors.WARNING
            + "(falta el parámetro '--destination_folder')"
            + bcolors.ENDC
            + " para el documento anonimizado o la carpeta destino no existe."
        )
        return False

    return True


def get_text_from_file(origin_path, file_name, column_to_use, include_titles):
    """
    :param origin_path: Path to the file to be used.
    :param file_name: Name of the file that contains the needed text.
    :param column_to_use: Column that contains the text to be used, indicate the column index (consider that the first index is zero).
    :return: Text obtained from the column from the file.
    """
    file_path = origin_path + file_name
    with open(file_path, "r") as file:
        columns = []
        reader = csv.reader(file)
        if include_titles:
            next(reader)

        for row in reader:
            only_included_cols = row[column_to_use]
            columns.append(only_included_cols)

        return columns


def get_epof():
    return get_text_from_file(EPOF_FOLDER, EPOF_FILE_NAME, EPOF_COLUMN_TO_USE, EPOF_INCLUDE_TITLES)


def get_matriculas_nbors():
    return get_text_from_file(
        MATRICULAS_FOLDER, MATRICULAS_FILE_NAME, MATRICULAS_COLUMN_TO_USE, MATRICULAS_INCLUDE_TITLES
    )


def save_anonymized_file(origin_path, filename, doc, destination_folder, save_txt_file, include_title):
    """
    We copy the original csv file content and we add the anonymized texts in a new column added to the end.
    :param origin_path: Path to the file that has been anonymized.
    :param filename: name of the file that has been anonymized.
    :param doc: doc text anonymized.
    :param destination_folder: Path where the csv file is going to be saved.
    :param save_txt_file: Flag that indicates if the file to be saved is txt.
    """
    if save_txt_file:
        file_name = filename
        with open(destination_folder + "/" + file_name, "w") as file:
            file.write(doc)
    else:
        name, _ = filename.split(".")
        file_name = name + "_anonimizado.csv"
        with open(origin_path + "/" + filename, "r") as csvinput:
            with open(destination_folder + "/" + file_name, "w") as csvoutput:
                writer = csv.writer(csvoutput, lineterminator="\n")
                reader = csv.reader(csvinput)

                all = []
                if include_title:
                    row = next(reader)
                    row.append("texto_anonimizado")
                    all.append(row)

                for idx, row in enumerate(reader):
                    row.append(doc[idx])
                    all.append(row)

                writer.writerows(all)

    logger.info(f"Se guardó el archivo {file_name} en la carpeta {destination_folder}")


def generate_csv_file(result, destination_folder, results_file_name, logger):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    results_file_name = results_file_name + ".csv" if results_file_name else DEFAULT_EVALUATE_EFFICIENCY_FILE_NAME
    path = f"{dir_path}/{destination_folder}/{results_file_name}"
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
                "Entidad": item.get("entity"),
                "Modelo": item.get("model"),
                "Esperado": item.get("expected"),
                "Efectividad": item.get("efficiency"),
            }
        )

    # opening the csv file in 'w' mode
    file = open(path, "w", newline="")
    with file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
