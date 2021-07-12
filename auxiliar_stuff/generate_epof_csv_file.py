import json
import csv

# json obtained from https://spreadsheets.google.com/feeds/list/1LleEbm1W8YyLDRTh-xQr0E7s42oc7oWNjodsTqanq9M/1/public/values?alt=json
with open("listado_epof.json", "r") as f:
    enfermedades = []
    json = json.load(f)
    data = json["feed"]["entry"]
    for entry in data:
        enf = entry["gsx$nombre"]["$t"]
        if "Nombre" not in enf:
            enfermedades.append({"enfermedad": enf})

file = open("./epof.csv", "w", newline="")
with file:
    writer = csv.DictWriter(file, fieldnames=["enfermedad"])
    writer.writeheader()
    for r in enfermedades:
        writer.writerow(r)
