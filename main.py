from processor import process_input_csv, write_result_csv
from service_ibge import fetch_ibge_municipios, build_municipios_index


INPUT_FILE = "input.csv"
OUTPUT_FILE = "resultado.csv"


def main():
    try:
        municipios = fetch_ibge_municipios()
        municipios_index = build_municipios_index(municipios)

        resultados = process_input_csv(INPUT_FILE, municipios_index)
        write_result_csv(OUTPUT_FILE, resultados)

        print(f"Arquivo '{OUTPUT_FILE}' gerado com sucesso.")
        print("Resumo:")
        for item in resultados:
            print(
                f"{item.municipio_input} -> "
                f"{item.municipio_ibge or 'N/A'} | "
                f"{item.uf or 'N/A'} | "
                f"{item.regiao or 'N/A'} | "
                f"{item.id_ibge or 'N/A'} | "
                f"{item.status}"
            )

    except Exception as error:
        print(f"Erro durante a execução: {error}")


if __name__ == "__main__":
    main()