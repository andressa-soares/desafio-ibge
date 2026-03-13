# Notas Explicativas

## Visão geral da solução

O programa foi desenvolvido em Python com o objetivo de processar um
arquivo CSV contendo municípios e populações, enriquecer esses dados com
informações oficiais da API de localidades do IBGE e gerar dois
artefatos de saída: um arquivo detalhado com o resultado do
processamento (`resultado.csv`) e um arquivo com estatísticas
consolidadas (`estatistica.json`).

A solução segue o fluxo abaixo:

1.  leitura do arquivo `input.csv`
2.  consumo da API do IBGE para obter todos os municípios
3.  normalização e busca dos municípios informados no CSV
4.  geração do arquivo `resultado.csv`
5.  cálculo das estatísticas solicitadas
6.  geração do arquivo `estatistica.json`

------------------------------------------------------------------------

## Estrutura do projeto

O código foi organizado em módulos para separar responsabilidades e
facilitar manutenção:

-   **models.py**\
    Define a estrutura `MunicipioResultado`, utilizada para representar
    cada linha processada.

-   **service_ibge.py**\
    Responsável por consumir a API do IBGE, normalizar nomes e realizar
    o processo de busca dos municípios.

-   **processor.py**\
    Contém a lógica de processamento do arquivo de entrada, geração do
    arquivo de resultado e cálculo das estatísticas.

-   **main.py**\
    Coordena o fluxo completo da aplicação.

Essa separação melhora a legibilidade do código e facilita futuras
evoluções.

------------------------------------------------------------------------

## Consumo da API do IBGE

A solução utiliza a API pública:

https://servicodados.ibge.gov.br/api/v1/localidades/municipios

A estratégia adotada foi realizar **uma única requisição para obter
todos os municípios** e armazená-los em memória. A partir dessa lista é
criado um índice normalizado que permite realizar buscas rápidas.

Essa abordagem reduz o número de chamadas HTTP e evita dependência da
API para cada município individual.

------------------------------------------------------------------------

## Normalização dos nomes

Os nomes presentes no arquivo CSV podem não seguir exatamente o mesmo
padrão da base do IBGE. Para lidar com isso foi implementado um processo
de normalização que:

-   converte o texto para minúsculas
-   remove acentos
-   remove caracteres especiais
-   remove espaços extras

Exemplo:

Niteroi → niteroi\
Niterói → niteroi\
São Paulo → sao paulo

Essa normalização permite comparar corretamente os nomes mesmo quando
existem pequenas diferenças de escrita.

------------------------------------------------------------------------

## Estratégia de matching

A busca de municípios ocorre em duas etapas:

1.  comparação exata após normalização
2.  comparação aproximada utilizando `SequenceMatcher`

Essa segunda etapa permite identificar municípios mesmo quando há
pequenos erros de digitação.

A lógica adotada foi:

-   **OK** → quando existe um único município correspondente
-   **AMBIGUO** → quando existem múltiplos municípios possíveis
-   **NAO_ENCONTRADO** → quando não há correspondência confiável
-   **ERRO_API** → quando ocorre falha na integração com a API do IBGE

A comparação aproximada foi configurada de forma conservadora para
evitar correspondências incorretas.

------------------------------------------------------------------------

## Tratamento de erros da API

Foi implementado tratamento para possíveis falhas na integração com a
API do IBGE, como:

-   timeout
-   erro HTTP
-   resposta inválida

Caso a API esteja indisponível, o programa não interrompe a execução. Em
vez disso, todos os registros são marcados com o status `ERRO_API`. Isso
garante que os arquivos de saída ainda sejam gerados e permite
identificar claramente que o problema ocorreu na integração externa.

------------------------------------------------------------------------

## Geração do arquivo resultado.csv

Após o processamento, o programa gera o arquivo `resultado.csv` com as
colunas:

-   municipio_input
-   populacao_input
-   municipio_ibge
-   uf
-   regiao
-   id_ibge
-   status

Cada linha representa o resultado do enriquecimento de um município
presente no arquivo de entrada.

------------------------------------------------------------------------

## Cálculo das estatísticas

As estatísticas são calculadas a partir dos registros processados.

Os indicadores gerados são:

-   **total_municipios** -- número total de municípios processados
-   **total_ok** -- quantidade de municípios encontrados com sucesso
-   **total_nao_encontrado** -- quantidade de municípios sem
    correspondência
-   **total_erro_api** -- quantidade de registros afetados por falha na
    API
-   **pop_total_ok** -- soma da população apenas dos municípios com
    status OK
-   **medias_por_regiao** -- média da população por região considerando
    apenas municípios com status OK

As médias por região são ordenadas do maior para o menor valor para
facilitar a leitura do resultado.

------------------------------------------------------------------------

## Geração do arquivo estatistica.json

Após o cálculo das métricas, o programa gera o arquivo
`estatistica.json` no formato exigido pela API de correção:

{ "stats": { ... } }

Esse arquivo é utilizado posteriormente para envio dos resultados para a
função de avaliação.

------------------------------------------------------------------------

## Execução do programa

Para executar o projeto:

python main.py

A execução realiza:

1.  consumo da API do IBGE
2.  processamento do arquivo `input.csv`
3.  geração do `resultado.csv`
4.  cálculo das estatísticas
5.  geração do `estatistica.json`