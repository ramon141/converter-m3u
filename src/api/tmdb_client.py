import requests
import time
from config.settings import (
    API_KEY, BEARER_TOKEN, MAX_RETRIES, 
    TMDB_SEARCH_MOVIE, TMDB_SEARCH_TV,
    TMDB_MOVIE_EXTERNAL_IDS, TMDB_TV_EXTERNAL_IDS,
    DEFAULT_LANGUAGE
)

class TMDbClient:
    """
    Cliente para a API do TMDb (The Movie Database)
    """
    def __init__(self, api_key=None, bearer_token=None):
        self.api_key = api_key or API_KEY
        self.bearer_token = bearer_token or BEARER_TOKEN
        
    def make_request_with_retry(self, url, params=None, headers=None, max_retries=MAX_RETRIES):
        """
        Faz uma requisição com retry em caso de erro 429 (Too Many Requests)
        """
        attempt = 0
        while attempt < max_retries:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 30))
                print(f"\nRecebeu erro 429. Esperando {retry_after} segundos antes de tentar novamente...")
                time.sleep(retry_after)
                attempt += 1
            else:
                return response
        print(f"\nMáximo de tentativas alcançado para a URL: {url}")
        return None
    
    def search_media(self, name, is_series=False, language=DEFAULT_LANGUAGE):
        """
        Procura por um filme ou série pelo nome
        """
        search_url = TMDB_SEARCH_TV if is_series else TMDB_SEARCH_MOVIE
        search_params = {"api_key": self.api_key, "query": name, "language": language}
        
        response = self.make_request_with_retry(search_url, params=search_params)
        
        if response and response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                return results[0]["id"]
        return None
    
    def get_external_ids(self, tmdb_id, is_series=False):
        """
        Obtém os IDs externos (como IMDb) para um filme ou série
        """
        if not tmdb_id:
            return None
            
        external_ids_url = TMDB_TV_EXTERNAL_IDS.format(tmdb_id=tmdb_id) if is_series else TMDB_MOVIE_EXTERNAL_IDS.format(tmdb_id=tmdb_id)
        
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "accept": "application/json"
        }
        
        response = self.make_request_with_retry(external_ids_url, headers=headers)
        
        if response and response.status_code == 200:
            return response.json().get("imdb_id")
        return None
        
    def get_imdb_id(self, name, is_series=False):
        """
        Obtém o IMDb ID para um filme ou série
        """
        tmdb_id = self.search_media(name, is_series)
        if tmdb_id:
            return self.get_external_ids(tmdb_id, is_series)
        print(f"IMDb ID não encontrado para: {name}")
        return None 