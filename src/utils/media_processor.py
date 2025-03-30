from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from src.api.tmdb_client import TMDbClient
from src.cache.cache_manager import CacheManager
from config.settings import MAX_WORKERS

class MediaProcessor:
    """
    Classe para processar entradas de mídia e buscar os IMDb IDs
    """
    def __init__(self, verbose=False):
        self.tmdb_client = TMDbClient(verbose=verbose)
        self.cache_manager = CacheManager()
        self.verbose = verbose
    
    def _process_entry(self, entry):
        """
        Processa uma entrada de mídia para buscar o IMDb ID
        """
        name = entry.name
        is_series = entry.is_series
        
        # Verifica se já temos o ID no cache
        if self.cache_manager.has_id(name):
            imdb_id = self.cache_manager.get_id(name)
            if self.verbose:
                print(f"Usando IMDb ID do cache para: {name}")
            
            # Se o ID no cache não for None, atualiza a entrada
            if imdb_id is not None:
                entry.set_imdb_id(imdb_id)
                return entry
            
            # Se o ID no cache for None, significa que já buscamos e não encontramos
            # então retorna None para não incluir no resultado
            if self.verbose:
                print(f"ID no cache é null para: {name}, já buscado anteriormente")
            return None
        
        # Busca o IMDb ID na API
        imdb_id = self.tmdb_client.get_imdb_id(name, is_series)
        
        # Atualiza o cache em todos os casos, mesmo quando o ID não for encontrado
        self.cache_manager.set_id(name, imdb_id)
        
        # Se encontrou o ID, atualiza a entrada e retorna
        if imdb_id:
            entry.set_imdb_id(imdb_id)
            return entry
        
        # Não encontrou o ID, então não inclui no resultado
        return None
    
    def process_entries(self, entries):
        """
        Processa uma lista de entradas de mídia em paralelo
        """
        valid_entries = []
        
        # Processa as entradas em paralelo
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for result in tqdm(
                executor.map(self._process_entry, entries), 
                total=len(entries), 
                desc="Consultando TMDb"
            ):
                if result:
                    valid_entries.append(result)
        
        # Forçar o salvamento do cache ao final do processamento
        self.cache_manager.save_cache(force=True)
        
        return valid_entries 