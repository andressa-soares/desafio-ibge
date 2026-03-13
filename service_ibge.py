import re

import requests
import unicodedata
from difflib import get_close_matches

IBGE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

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
    response = requests.get(IBGE_URL, timeout=30)
    response.raise_for_status()
    return response.json()


def build_municipios_index(municipios: list[dict]) -> dict[str, dict]:
    index = {}

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

        # Se houver duplicidade após normalização, guardamos em lista
        # para poder detectar possível ambiguidade.
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

    return index


def find_best_match(municipio_input: str, municipios_index: dict[str, list[dict]]) -> tuple[str, dict | None]:
    """
    Retorna:
    - status: OK | NAO_ENCONTRADO | AMBIGUO
    - dados do município encontrado ou None
    """
    normalized_input = normalize_text(municipio_input)

    # 1) Match exato após normalização
    exact_matches = municipios_index.get(normalized_input)
    if exact_matches:
        if len(exact_matches) == 1:
            return "OK", exact_matches[0]
        return "AMBIGUO", None

    # 2) Match aproximado
    all_keys = list(municipios_index.keys())
    close_matches = get_close_matches(normalized_input, all_keys, n=3, cutoff=0.84)

    if not close_matches:
        return "NAO_ENCONTRADO", None

    # Se vier mais de uma possibilidade muito parecida, marcamos como ambíguo
    if len(close_matches) > 1:
        first = close_matches[0]
        second = close_matches[1]

        # Se ambos existirem e estiverem muito próximos em "força" de match,
        # preferimos ser conservadores.
        if abs(len(first) - len(second)) <= 1:
            if first[:3] == second[:3]:
                return "AMBIGUO", None

    selected_key = close_matches[0]
    selected_matches = municipios_index.get(selected_key, [])

    if len(selected_matches) == 1:
        return "OK", selected_matches[0]

    if len(selected_matches) > 1:
        return "AMBIGUO", None

    return "NAO_ENCONTRADO", None