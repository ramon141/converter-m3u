from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from src.api.tmdb_client import TMDbClient
from src.cache.cache_manager import CacheManager
from config.settings import MAX_WORKERS

class MediaProcessor:
    """
    Classe para processar entradas de mídia e buscar os IMDb IDs
    """
    def __init__(self):
        self.tmdb_client = TMDbClient()
        self.cache_manager = CacheManager()
    
    def _process_entry(self, entry):
        """
        Processa uma entrada de mídia para buscar o IMDb ID
        """
        name = entry.name
        is_series = entry.is_series
        
        # Verifica se já temos o ID no cache
        if self.cache_manager.has_id(name):
            imdb_id = self.cache_manager.get_id(name)
            entry.set_imdb_id(imdb_id)
            return entry
        
        # Busca o IMDb ID na API
        imdb_id = self.tmdb_client.get_imdb_id(name, is_series)
        
        if imdb_id:
            # Atualiza o cache e a entrada
            self.cache_manager.set_id(name, imdb_id)
            entry.set_imdb_id(imdb_id)
            return entry
        
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
        
        # Salva o cache atualizado
        self.cache_manager.save_cache()
        
        return valid_entries 