import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configurações da API
API_KEY = os.getenv('API_KEY')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

# Configurações de cache
CACHE_FILE = os.getenv('CACHE_FILE', 'cache_ids.json')
CACHE_DIR = 'cache'

# Configurações do parser
DEFAULT_INPUT_FILE = "input.m3u"
DEFAULT_OUTPUT_FILE = "output.json"

# Configurações da API do TMDb
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_SEARCH_MOVIE = f"{TMDB_BASE_URL}/search/movie"
TMDB_SEARCH_TV = f"{TMDB_BASE_URL}/search/tv"
TMDB_MOVIE_EXTERNAL_IDS = f"{TMDB_BASE_URL}/movie/{{tmdb_id}}/external_ids"
TMDB_TV_EXTERNAL_IDS = f"{TMDB_BASE_URL}/tv/{{tmdb_id}}/external_ids"
DEFAULT_LANGUAGE = "pt-br"

# Configurações de requisição
MAX_RETRIES = 5
MAX_WORKERS = 5 