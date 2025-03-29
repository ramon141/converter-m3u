# Conversor M3U

Um conversor de arquivos M3U para JSON com busca de IMDb IDs utilizando a API do TMDb.

## Estrutura do Projeto

```
├── config/             # Configurações do projeto
│   ├── __init__.py
│   └── settings.py     # Configurações e constantes
├── src/                # Código-fonte
│   ├── __init__.py
│   ├── api/            # Componentes de API
│   │   ├── __init__.py
│   │   └── tmdb_client.py
│   ├── cache/          # Gerenciamento de cache
│   │   ├── __init__.py
│   │   └── cache_manager.py
│   ├── models/         # Modelos de dados
│   │   ├── __init__.py
│   │   └── media_entry.py
│   ├── parsers/        # Analisadores de arquivos
│   │   ├── __init__.py
│   │   └── m3u_parser.py
│   └── utils/          # Utilitários
│       ├── __init__.py
│       ├── json_exporter.py
│       ├── media_processor.py
│       └── text_cleaner.py
├── .env                # Arquivo de variáveis de ambiente (não versionado)
├── .gitignore          # Arquivo de configuração do Git
├── main.py             # Ponto de entrada do aplicativo
└── README.md           # Documentação do projeto
```

## Requisitos

- Python 3.6+
- Bibliotecas: requests, python-dotenv, tqdm

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/converter-m3u.git
cd converter-m3u
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo `.env` com suas credenciais:
```
API_KEY=sua_chave_api_tmdb
BEARER_TOKEN=seu_token_bearer_tmdb
CACHE_FILE=cache_ids.json
```

## Uso

Para converter um arquivo M3U para JSON:

```bash
python main.py -i seu_arquivo.m3u -o saida.json
```

Ou use os valores padrão (input.m3u e output.json):

```bash
python main.py
```

## Como Funciona

1. O programa lê um arquivo M3U contendo entradas de filmes e séries.
2. Para cada entrada, ele limpa o nome e identifica se é uma série ou filme.
3. Usando a API do TMDb, o programa busca o IMDb ID correspondente.
4. Os resultados são salvos em um arquivo JSON.
5. Um cache é utilizado para evitar requisições repetidas à API. 