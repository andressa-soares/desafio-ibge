from processor import (
    process_input_csv,
    write_result_csv,
    calculate_stats,
    write_stats_json,
)
from service_ibge import fetch_ibge_municipios, build_municipios_index


INPUT_FILE = "input.csv"
RESULTADO_FILE = "resultado.csv"
ESTATISTICA_FILE = "estatistica.json"


def main():
    try:
        municipios = fetch_ibge_municipios()
        municipios_index = build_municipios_index(municipios)

        resultados = process_input_csv(INPUT_FILE, municipios_index)
        write_result_csv(RESULTADO_FILE, resultados)

        stats = calculate_stats(resultados)
        write_stats_json(ESTATISTICA_FILE, stats)

        print(f"Arquivo '{RESULTADO_FILE}' gerado com sucesso.")
        print(f"Arquivo '{ESTATISTICA_FILE}' gerado com sucesso.")
        print("Estatísticas:")
        print(stats)

    except Exception as error:
        print(f"Erro durante a execução: {error}")


if __name__ == "__main__":
    main()