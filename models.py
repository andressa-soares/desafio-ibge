from dataclasses import dataclass, asdict


@dataclass
class MunicipioResultado:
    municipio_input: str
    populacao_input: int
    municipio_ibge: str
    uf: str
    regiao: str
    id_ibge: str
    status: str

    def to_dict(self) -> dict:
        return asdict(self)