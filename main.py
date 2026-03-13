from processor import (
    process_input_csv,
    process_input_csv_with_api_error,
    write_result_csv,
    calculate_stats,
    write_stats_json,
)
from service_ibge import (
    fetch_ibge_municipios,
    build_municipios_index,
    IbgeApiError,
)


INPUT_FILE = "input.csv"
RESULTADO_FILE = "resultado.csv"
ESTATISTICA_FILE = "estatistica.json"


def log_info(message: str) -> None:
    print(f"[INFO] {message}")


def log_error(message: str) -> None:
    print(f"[ERROR] {message}")


def main():
    log_info("Iniciando processamento do desafio técnico.")

    try:
        municipios = fetch_ibge_municipios()
        municipios_index = build_municipios_index(municipios)
        resultados = process_input_csv(INPUT_FILE, municipios_index)

    except IbgeApiError as error:
        log_error(f"Falha na integração com a API do IBGE: {error}")
        log_info("Continuando execução com status ERRO_API para todos os registros.")
        resultados = process_input_csv_with_api_error(INPUT_FILE)

    except FileNotFoundError:
        log_error(f"Arquivo de entrada '{INPUT_FILE}' não encontrado.")
        return

    except Exception as error:
        log_error(f"Erro inesperado durante a execução: {error}")
        return

    write_result_csv(RESULTADO_FILE, resultados)

    stats = calculate_stats(resultados)
    write_stats_json(ESTATISTICA_FILE, stats)

    log_info(f"Arquivo '{RESULTADO_FILE}' gerado com sucesso.")
    log_info(f"Arquivo '{ESTATISTICA_FILE}' gerado com sucesso.")
    log_info(f"Estatísticas finais: {stats}")
    log_info("Processamento finalizado com sucesso.")


if __name__ == "__main__":
    main()