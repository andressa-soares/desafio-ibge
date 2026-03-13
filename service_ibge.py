import re
import requests
import unicodedata
from difflib import SequenceMatcher

IBGE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"


class IbgeApiError(Exception):
    """Erro de integração com a API do IBGE."""


def log_info(message: str) -> None:
    print(f"[INFO] {message}")


def log_error(message: str) -> None:
    print(f"[ERROR] {message}")


def normalize_text(text: str) -> str:
    if text is None:
        return ""

    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = " ".join(text.split())

    return text


def fetch_ibge_municipios() -> list[dict]:
    log_info(f"Consumindo API do IBGE: {IBGE_URL}")

    try:
        response = requests.get(IBGE_URL, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            raise IbgeApiError("Resposta da API do IBGE não está no formato esperado.")

        log_info(f"API do IBGE retornou {len(data)} municípios.")
        return data

    except requests.exceptions.Timeout as exc:
        log_error("Timeout ao consumir a API do IBGE.")
        raise IbgeApiError("Timeout ao consumir a API do IBGE.") from exc

    except requests.exceptions.RequestException as exc:
        log_error(f"Falha HTTP ao consumir a API do IBGE: {exc}")
        raise IbgeApiError("Falha HTTP ao consumir a API do IBGE.") from exc

    except ValueError as exc:
        log_error("Falha ao converter resposta da API do IBGE para JSON.")
        raise IbgeApiError("Resposta inválida da API do IBGE.") from exc


def build_municipios_index(municipios: list[dict]) -> dict[str, list[dict]]:
    log_info("Montando índice normalizado de municípios do IBGE.")

    index: dict[str, list[dict]] = {}

    for item in municipios:
        nome = item.get("nome", "")

        uf = (
            item.get("regiao-imediata", {})
            .get("regiao-intermediaria", {})
            .get("UF", {})
            .get("sigla", "")
        )

        regiao = (
            item.get("regiao-imediata", {})
            .get("regiao-intermediaria", {})
            .get("UF", {})
            .get("regiao", {})
            .get("nome", "")
        )

        id_ibge = item.get("id", "")

        normalized_name = normalize_text(nome)

        if normalized_name not in index:
            index[normalized_name] = []

        index[normalized_name].append(
            {
                "municipio_ibge": nome,
                "uf": uf,
                "regiao": regiao,
                "id_ibge": str(id_ibge),
            }
        )

    log_info(f"Índice montado com {len(index)} chaves normalizadas.")
    return index


def calculate_similarity(text_a: str, text_b: str) -> float:
    return SequenceMatcher(None, text_a, text_b).ratio()


def find_best_match(
    municipio_input: str,
    municipios_index: dict[str, list[dict]],
    similarity_threshold: float = 0.90,
    ambiguity_margin: float = 0.02,
) -> tuple[str, dict | None]:
    """
    Regras:
    - Match exato normalizado:
        - 1 resultado -> OK
        - mais de 1 resultado -> AMBIGUO
    - Match aproximado:
        - 1 candidato confiável -> OK
        - mais de 1 candidato muito próximo -> NAO_ENCONTRADO
        - nenhum candidato confiável -> NAO_ENCONTRADO

    Observação:
    - AMBIGUO só representa múltiplos resultados reais.
    - Similaridade incerta não vira AMBIGUO; vira NAO_ENCONTRADO.
    """
    normalized_input = normalize_text(municipio_input)

    # 1) Match exato após normalização
    exact_matches = municipios_index.get(normalized_input)
    if exact_matches:
        if len(exact_matches) == 1:
            return "OK", exact_matches[0]
        return "AMBIGUO", None

    # 2) Match aproximado
    scored_candidates = []
    for normalized_name in municipios_index.keys():
        score = calculate_similarity(normalized_input, normalized_name)
        if score >= similarity_threshold:
            scored_candidates.append((normalized_name, score))

    if not scored_candidates:
        return "NAO_ENCONTRADO", None

    scored_candidates.sort(key=lambda item: item[1], reverse=True)

    best_key, best_score = scored_candidates[0]

    if len(scored_candidates) > 1:
        _, second_score = scored_candidates[1]

        # Se os dois melhores candidatos estão muito próximos,
        # não é confiável assumir um match.
        if second_score >= best_score - ambiguity_margin:
            return "NAO_ENCONTRADO", None

    selected_matches = municipios_index.get(best_key, [])

    if len(selected_matches) == 1:
        return "OK", selected_matches[0]

    if len(selected_matches) > 1:
        return "AMBIGUO", None

    return "NAO_ENCONTRADO", None