import os
import sys
import argparse
from time import time
from utils import (
    bcolors,
    create_logger,
    check_dir,
    generate_csv_file,
    save_anonymized_file,
    are_parameters_ok_to_anonymize,
    are_parameters_ok_to_evaluate_efficiency,
    get_text_from_file,
)
from model_utils import Nlp, get_comparison_result, anonymize_text

logger = create_logger()
DEFAULT_FILE_NAME = "texto_anonimizado.txt"
MODEL_NAME = "es_core_news_lg"  # Sólo detecta: LOC, MISC, ORG, PER


def anonymize_doc(
    text=None, save_file=False, origin_path=None, file_name=False, column_to_use=None, destination_folder=None
):
    """
    :param text: Text to be anonymized.
    :param save_file: Flag that indicates if the user wants to save the file or not.
    :param origin_path: Path to the file to be anonymized.
    :param file_name: The filename from the file to be anonymized
    :param column_to_use: Column to use from the file (only one), indicate it position (consider that the first index is zero)
    :param destination_folder: Path where the anonymized file is going to be saved.
    :return: Anonymized text when is not saved to a file.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("function", help="To anonymize you should call anonymize_doc", type=str)
    parser.add_argument("--text", help="The text to be anonymized", type=str)
    parser.add_argument(
        "--save_file", help="Would you like to save a file or show results in the console?", action="store_true"
    )
    parser.add_argument("--origin_path", help="Path to the file to be anonymized", type=str)
    parser.add_argument("--file_name", help="The filename from the file to be anonymized", type=str)
    parser.add_argument(
        "--column_to_use",
        help="Column to use from the file (only one), indicate it position (consider that the first index is zero)",
        type=int,
    )
    parser.add_argument("--include_titles", help="Does the file to be anonymized include titles?", action="store_true")
    parser.add_argument("--destination_folder", help="Path where the anonymized file is going to be saved", type=str)
    args = parser.parse_args()

    can_execute = are_parameters_ok_to_anonymize(args)

    if can_execute:
        start = time()
        anonymization_output = (
            f"guardará en la carpeta: {args.destination_folder}"
            if args.destination_folder
            else "mostrará en la consola"
        )

        if args.text:
            to_anonymize_label = "texto"
            to_anonymize = args.text
        else:
            to_anonymize_label = "archivo"
            to_anonymize = args.file_name

        logger.info(
            f"""Anonimizando el {to_anonymize_label}: {to_anonymize}.
                        \nEl resultado de la anonimización se {anonymization_output}."""
        )

        nlp = Nlp(MODEL_NAME)

        if args.text:
            anonymized_docs = anonymize_text(nlp, args.text, not args.save_file)
        else:
            doc_text = get_text_from_file(args.origin_path, args.file_name, args.column_to_use, args.include_titles)
            anonymized_docs = []
            for text in doc_text:
                anonymized_text = anonymize_text(nlp, text, not args.save_file)
                anonymized_docs.append(anonymized_text)

        if args.save_file:
            save_anonymized_file(
                args.origin_path,
                args.file_name or DEFAULT_FILE_NAME,
                anonymized_docs,
                args.destination_folder,
                True if args.text else False,
            )
        elif type(anonymized_docs) == list:
            print(
                f"""
                \n
                {bcolors.WARNING}
                El texto anonimizado tiene varias filas, recomendamos guardarlo como archivo.
                {bcolors.ENDC}
            """
            )
            print("\n" + bcolors.OKGREEN + "Texto anonimizado:" + bcolors.ENDC + f" \n{anonymized_docs}")
        else:
            print("\n" + bcolors.OKGREEN + "Texto anonimizado:" + bcolors.ENDC + f" \n{anonymized_docs}")

        logger.info(f"Anonimización finalizada en {time() - start} segundos.")
        return anonymized_docs
    else:
        print(
            f"""
Revise los parámetros enviados para poder anonimizar. Para más información consulte la ayuda:
{bcolors.WARNING}'python tasks.py anonymize_doc --help'{bcolors.ENDC}.
        """
        )


def evaluate_efficiency(
    origin_path=None,
    file_name=None,
    column_to_use=None,
    json_origin_path=None,
    json_file_name=None,
    destination_folder=None,
):
    """
    :param origin_path: Path to the file to be anonymized on the way to evaluate efficiency.
    :param file_name: The filename from the file to be anonymized on the way to evaluate efficiency.
    :param column_to_use: Column to use from the file (only one), indicate it position (consider that the first index is zero).
    :param json_origin_path: Path to the json file with the annotations from the document previously indicated.
    :param json_file_name: The filename from the json file with the annotations from the document previously indicated (MUST be json).
    :param destination_folder: Path where the comparison between the anonymization and the annotations will be saved. The file will be called results.csv.
    :return: Notification when the process is finished.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "function", help="To evaluate the efficiency of the model you should call evaluate_efficiency", type=str
    )
    parser.add_argument(
        "--origin_path", help="Path to the file to be anonymized on the way to evaluate efficiency", type=str
    )
    parser.add_argument(
        "--file_name", help="The filename from the file to be anonymized on the way to evaluate efficiency", type=str
    )
    parser.add_argument(
        "--column_to_use",
        help="Column to use from the file (only one), indicate it position (consider that the first index is zero)",
        type=int,
    )
    parser.add_argument(
        "--json_origin_path",
        help="Path to the json file with the annotations from the document previously indicated",
        type=str,
    )
    parser.add_argument(
        "--json_file_name",
        help="The filename from the json file with the annotations from the document previously indicated (MUST be json)",
        type=str,
    )
    parser.add_argument(
        "--destination_folder",
        help="Path where the comparison between the anonymization and the annotations will be saved. The file will be called results.csv.",
        type=str,
    )
    args = parser.parse_args()

    can_execute = are_parameters_ok_to_evaluate_efficiency(args)

    if can_execute:
        start = time()
        logger.info(
            f"""Analizando el documento: {origin_path+"/"+file_name} junto al archivo de anotaciones: {json_origin_path+"/"+json_file_name}.
                        \nEl resultado del análisis se guardará en la carpeta: {destination_folder}."""
        )

        nlp = Nlp(MODEL_NAME)

        annotations = ""
        doc_text = "texto de ejemplo"
        result = get_comparison_result(nlp, doc_text, annotations)
        generate_csv_file(result, destination_folder, logger)

        print(f"Proceso terminado en {time() - start} segundos.")
        logger.info(f"Evaluación de eficiencia al anonimizar finalizada en {time() - start} segundos.")
    else:
        print(
            f"""
Revise los parámetros enviados para realizar la evaluación de eficiencia. Para más información consulte la ayuda:
{bcolors.WARNING}'python tasks.py evaluate_efficiency --help'{bcolors.ENDC}.
        """
        )


if __name__ == "__main__":
    args = sys.argv
    if len(args) <= 1:
        print(
            f"{bcolors.WARNING}Debe ingresar una función a ejecutar y los parámetros correspondientes.{bcolors.ENDC}\nPor ejemplo: python tasks.py anonymize_doc --help"
        )
    else:
        # args[0] = current file
        # args[1] = function name
        # args[2] = function args: (*unpacked)
        globals()[args[1]](*args[2:])
