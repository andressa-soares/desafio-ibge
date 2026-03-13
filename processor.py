import csv
import json
from typing import List

from models import MunicipioResultado
from service_ibge import find_best_match


STATUS_OK = "OK"
STATUS_NAO_ENCONTRADO = "NAO_ENCONTRADO"
STATUS_ERRO_API = "ERRO_API"
STATUS_AMBIGUO = "AMBIGUO"


def log_info(message: str) -> None:
    print(f"[INFO] {message}")


def process_input_csv(input_file_path: str, municipios_index: dict) -> List[MunicipioResultado]:
    log_info(f"Lendo arquivo de entrada: {input_file_path}")
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

    log_info(f"Processamento concluído com {len(resultados)} registros.")
    return resultados


def process_input_csv_with_api_error(input_file_path: str) -> List[MunicipioResultado]:
    log_info("Processando arquivo com fallback de ERRO_API.")
    resultados = []

    with open(input_file_path, mode="r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            municipio_input = row["municipio"].strip()
            populacao_input = int(row["populacao"])

            resultados.append(
                MunicipioResultado(
                    municipio_input=municipio_input,
                    populacao_input=populacao_input,
                    municipio_ibge="",
                    uf="",
                    regiao="",
                    id_ibge="",
                    status=STATUS_ERRO_API,
                )
            )

    log_info(f"Fallback ERRO_API aplicado a {len(resultados)} registros.")
    return resultados


def write_result_csv(output_file_path: str, resultados: List[MunicipioResultado]) -> None:
    log_info(f"Gerando arquivo de resultado: {output_file_path}")

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


def calculate_stats(resultados: List[MunicipioResultado]) -> dict:
    total_municipios = len(resultados)
    total_ok = sum(1 for item in resultados if item.status == STATUS_OK)
    total_nao_encontrado = sum(1 for item in resultados if item.status == STATUS_NAO_ENCONTRADO)
    total_erro_api = sum(1 for item in resultados if item.status == STATUS_ERRO_API)

    ok_items = [item for item in resultados if item.status == STATUS_OK]
    pop_total_ok = sum(item.populacao_input for item in ok_items)

    soma_por_regiao = {}
    quantidade_por_regiao = {}

    for item in ok_items:
        regiao = item.regiao

        if regiao not in soma_por_regiao:
            soma_por_regiao[regiao] = 0
            quantidade_por_regiao[regiao] = 0

        soma_por_regiao[regiao] += item.populacao_input
        quantidade_por_regiao[regiao] += 1

    medias_por_regiao = {}
    for regiao, soma in soma_por_regiao.items():
        quantidade = quantidade_por_regiao[regiao]
        medias_por_regiao[regiao] = round(soma / quantidade, 2)

    medias_por_regiao = dict(
        sorted(
            medias_por_regiao.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )

    stats = {
        "stats": {
            "total_municipios": total_municipios,
            "total_ok": total_ok,
            "total_nao_encontrado": total_nao_encontrado,
            "total_erro_api": total_erro_api,
            "pop_total_ok": pop_total_ok,
            "medias_por_regiao": medias_por_regiao,
        }
    }

    log_info("Estatísticas calculadas com sucesso.")
    return stats


def write_stats_json(output_file_path: str, stats: dict) -> None:
    log_info(f"Gerando arquivo de estatísticas: {output_file_path}")

    with open(output_file_path, mode="w", encoding="utf-8") as jsonfile:
        json.dump(stats, jsonfile, ensure_ascii=False, indent=2)