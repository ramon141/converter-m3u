import json
import os
from config.settings import CACHE_FILE, CACHE_DIR

class CacheManager:
    """
    Classe para gerenciar o cache de IDs do TMDb para IMDb
    """
    def __init__(self, cache_file=None):
        self.cache_file = cache_file or CACHE_FILE
        self.ids = self._load_cache()
        
        # Garante que o diretório de cache existe
        os.makedirs(CACHE_DIR, exist_ok=True)
        
        # Se o caminho do arquivo não incluir o diretório, adiciona-o
        if not os.path.dirname(self.cache_file):
            self.cache_file = os.path.join(CACHE_DIR, self.cache_file)
    
    def _load_cache(self):
        """
        Carrega o cache do disco
        """
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
    
    def save_cache(self):
        """
        Salva o cache no disco
        """
        with open(self.cache_file, 'w', encoding='utf-8') as file:
            json.dump(self.ids, file, indent=4, ensure_ascii=False)
    
    def get_id(self, name):
        """
        Obtém o ID do cache
        """
        return self.ids.get(name)
    
    def set_id(self, name, imdb_id):
        """
        Define o ID no cache
        """
        self.ids[name] = imdb_id
    
    def has_id(self, name):
        """
        Verifica se o nome está no cache
        """
        return name in self.ids 