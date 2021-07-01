import sys
from sys import exit
from tasks import anonymize_doc, evaluate_efficiency


def print_menu():
	print("""
================================
	MENU
================================
1 - Anonimizar un documento
2 - Evaluar eficacia del modelo
3 - Salir
================================
Ingrese una opción y presione la tecla enter:
"""
)

def show_menu():

	print_menu()
	user_input = 0

	while user_input != 3:
		try:
			user_input = int(input())
		except:
			print("Debe ingresar una de las opciones listadas.")
			print_menu()

		if int(user_input) == 1:
			origin_path = input("Ingrese el path completo (nombre del archivo incluido) del documento a anonimizar y presione la tecla enter: \n")
			destination_folder = input("Ingrese el path completo de la carpeta donde el documento anonimizado será guardado y presione la tecla enter: \n")
			print(f"Se va a anonimizar el documento: {origin_path} \nSe guardará en la carpeta: {destination_folder}")
			anonymize_doc(origin_path, destination_folder)
			print_menu()
		elif int(user_input) == 2:
			doc_origin_path = input("Ingrese el path completo (nombre del archivo incluido) del documento a analizar y presione la tecla enter: \n")
			json_origin_path = input("Ingrese el path completo (nombre del archivo incluido) del archivo json con las anotaciones correspondientes al documento a analizar y presione la tecla enter: \n")
			destination_folder = input("Ingrese el path completo de la carpeta donde los resultados del cálculo de eficiencia serán guardados y presione la tecla enter: \n")
			print(f"Se va a analizar el documento: {doc_origin_path} \nSe guardará en la carpeta: {destination_folder}")
			
			evaluate_efficiency(doc_origin_path, json_origin_path, destination_folder)
			print_menu()
		elif int(user_input) == 3:
			print("Saliendo...")
			raise SystemExit

if __name__ == "__main__":
    show_menu()