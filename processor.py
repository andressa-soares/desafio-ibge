import csv
from typing import List

from models import MunicipioResultado
from service_ibge import find_best_match


STATUS_OK = "OK"
STATUS_NAO_ENCONTRADO = "NAO_ENCONTRADO"
STATUS_ERRO_API = "ERRO_API"
STATUS_AMBIGUO = "AMBIGUO"


def process_input_csv(input_file_path: str, municipios_index: dict) -> List[MunicipioResultado]:
    resultados = []

    with open(input_file_path, mode="r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            municipio_input = row["municipio"].strip()
            populacao_input = int(row["populacao"])

            status, match = find_best_match(municipio_input, municipios_index)

            if status == STATUS_OK and match:
                resultado = MunicipioResultado(
                    municipio_input=municipio_input,
                    populacao_input=populacao_input,
                    municipio_ibge=match["municipio_ibge"],
                    uf=match["uf"],
                    regiao=match["regiao"],
                    id_ibge=match["id_ibge"],
                    status=STATUS_OK,
                )
            elif status == STATUS_AMBIGUO:
                resultado = MunicipioResultado(
                    municipio_input=municipio_input,
                    populacao_input=populacao_input,
                    municipio_ibge="",
                    uf="",
                    regiao="",
                    id_ibge="",
                    status=STATUS_AMBIGUO,
                )
            else:
                resultado = MunicipioResultado(
                    municipio_input=municipio_input,
                    populacao_input=populacao_input,
                    municipio_ibge="",
                    uf="",
                    regiao="",
                    id_ibge="",
                    status=STATUS_NAO_ENCONTRADO,
                )

            resultados.append(resultado)

    return resultados


def write_result_csv(output_file_path: str, resultados: List[MunicipioResultado]) -> None:
    fieldnames = [
        "municipio_input",
        "populacao_input",
        "municipio_ibge",
        "uf",
        "regiao",
        "id_ibge",
        "status",
    ]

    with open(output_file_path, mode="w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for resultado in resultados:
            writer.writerow(resultado.to_dict())