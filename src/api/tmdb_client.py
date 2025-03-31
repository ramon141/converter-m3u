import requests
import time
import re
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
    def __init__(self, api_key=None, bearer_token=None, verbose=False):
        self.api_key = api_key or API_KEY
        self.bearer_token = bearer_token or BEARER_TOKEN
        self.verbose = verbose
        
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
    
    def search_media(self, name, is_series=False, language=DEFAULT_LANGUAGE, year=None):
        """
        Procura por um filme ou série pelo nome
        
        Args:
            name (str): Nome do filme ou série
            is_series (bool): Se é uma série ou não
            language (str): Idioma da busca
            year (int, optional): Ano de lançamento, se disponível
            
        Returns:
            int: ID do TMDb se encontrado, None caso contrário
        """
        search_url = TMDB_SEARCH_TV if is_series else TMDB_SEARCH_MOVIE
        search_params = {"api_key": self.api_key, "query": name, "language": language}
        
        # Se tiver o ano, adiciona ao parâmetro de busca
        if year:
            search_params["year"] = year
            
        if self.verbose:
            print(f"Buscando {'série' if is_series else 'filme'}: '{name}'{f' ({year})' if year else ''}")
        
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
    
    def _extract_year(self, name):
        """
        Extrai o ano do nome usando regex
        
        Args:
            name (str): Nome do filme ou série
            
        Returns:
            tuple: (Nome sem o ano, Ano extraído ou None)
        """
        # Procura por padrão de ano (1900-2099)
        year_match = re.search(r'(19\d{2}|20\d{2})', name)
        if year_match:
            year = int(year_match.group(1))
            # Remove o ano do nome
            clean_name = re.sub(r'\s*(19\d{2}|20\d{2})\s*', '', name).strip()
            if self.verbose:
                print(f"Detectado ano {year} no título: '{name}' -> '{clean_name}'")
            return clean_name, year
        return name, None
    
    def _handle_part_one(self, name):
        """
        Trata nomes que terminam com número 1
        
        Args:
            name (str): Nome do filme
            
        Returns:
            list: Lista de nomes alternativos para tentar
        """
        # Verifica se termina com " 1" ou similar
        if re.search(r'\s+1$', name):
            base_name = re.sub(r'\s+1$', '', name).strip()
            if self.verbose:
                print(f"Detectado filme parte 1: '{name}' -> Tentando também '{base_name}'")
            return [name, base_name]  # Tenta primeiro com o 1, depois sem
        return [name]  # Se não se aplica a regra, retorna só o nome original
    
    def _remove_4k(self, name):
        """
        Remove o sufixo 4K do nome do filme
        
        Args:
            name (str): Nome do filme
            
        Returns:
            tuple: (Nome sem 4K, Booleano indicando se a remoção ocorreu)
        """
        # Verifica se termina com " 4K" ou similar
        if re.search(r'\s+4K$', name, re.IGNORECASE):
            clean_name = re.sub(r'\s+4K$', '', name, flags=re.IGNORECASE).strip()
            if self.verbose:
                print(f"Detectado filme em 4K: '{name}' -> '{clean_name}'")
            return clean_name, True
        return name, False
    
    def get_imdb_id(self, name, is_series=False):
        """
        Obtém o IMDb ID para um filme ou série,
        tratando casos especiais como filmes com "1" no final,
        filmes com anos no título e filmes com "4K" no final.
        """
        # Primeiro remove o 4K, se presente
        name_without_4k, has_4k = self._remove_4k(name)
        
        # Extrai o ano se presente
        clean_name, year = self._extract_year(name_without_4k)
        
        # Se for série, não aplica as regras especiais
        if is_series:
            return self._search_with_alternatives(clean_name, is_series, year)
        
        # Para filmes, trata casos especiais
        name_variants = self._handle_part_one(clean_name)
        
        # Tenta cada variante do nome
        for variant in name_variants:
            imdb_id = self._search_with_alternatives(variant, is_series, year)
            if imdb_id:
                if self.verbose and (variant != name or has_4k):
                    print(f"Encontrado IMDb ID para '{variant}' em vez de '{name}'")
                return imdb_id
                
        if self.verbose:
            print(f"IMDb ID não encontrado após tentar todas as alternativas para: {name}")
        else:
            print(f"IMDb ID não encontrado para: {name}")
        return None
    
    def _search_with_alternatives(self, name, is_series=False, year=None):
        """
        Busca usando diferentes alternativas (com ano, sem ano, etc)
        
        Args:
            name (str): Nome a ser buscado
            is_series (bool): Se é série ou filme
            year (int, optional): Ano para filtrar, se disponível
            
        Returns:
            str: IMDb ID se encontrado, None caso contrário
        """
        # Primeira tentativa: com nome e ano (se disponível)
        if year:
            tmdb_id = self.search_media(name, is_series, year=year)
            if tmdb_id:
                imdb_id = self.get_external_ids(tmdb_id, is_series)
                if imdb_id:
                    if self.verbose:
                        print(f"Encontrado IMDb ID usando o ano {year} para: '{name}'")
                    return imdb_id
                elif self.verbose:
                    print(f"Encontrado TMDb ID, mas sem IMDb ID correspondente para: '{name}' (ano {year})")
            elif self.verbose:
                print(f"Não encontrado TMDb ID usando o ano {year} para: '{name}'")
        
        # Segunda tentativa: só com o nome
        tmdb_id = self.search_media(name, is_series)
        if tmdb_id:
            imdb_id = self.get_external_ids(tmdb_id, is_series)
            if imdb_id:
                if self.verbose and year:
                    print(f"Encontrado IMDb ID sem usar o ano para: '{name}'")
                return imdb_id
            elif self.verbose:
                print(f"Encontrado TMDb ID, mas sem IMDb ID correspondente para: '{name}'")
        elif self.verbose:
            print(f"Não encontrado TMDb ID para: '{name}'")
            
        return None 