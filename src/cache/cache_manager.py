import json
import os
import threading
import time
from config.settings import CACHE_FILE, CACHE_DIR

class CacheManager:
    """
    Classe para gerenciar o cache de IDs do TMDb para IMDb
    """
    def __init__(self, cache_file=None, save_interval=10):
        self.cache_file = cache_file or CACHE_FILE
        
        # Garante que o diretório de cache existe
        os.makedirs(CACHE_DIR, exist_ok=True)
        
        # Se o caminho do arquivo não incluir o diretório, adiciona-o
        if not os.path.dirname(self.cache_file):
            self.cache_file = os.path.join(CACHE_DIR, self.cache_file)
            
        # Carrega o cache existente (se houver)
        self.ids = self._load_cache()
            
        # Mutex para garantir acesso exclusivo durante a escrita
        self.mutex = threading.Lock()
        # Contador de alterações não salvas
        self.changes = 0
        # Intervalo de salvamento (número de alterações)
        self.save_interval = save_interval
        # Timestamp da última salvagem
        self.last_save = time.time()
        # Tempo máximo entre salvamentos (em segundos)
        self.max_time_between_saves = 30
    
    def _load_cache(self):
        """
        Carrega o cache do disco
        """
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as file:
                print(f"Carregando cache existente de: {self.cache_file}")
                return json.load(file)
        except FileNotFoundError:
            print(f"Arquivo de cache não encontrado em: {self.cache_file}. Criando novo cache.")
            return {}
        except json.JSONDecodeError:
            print(f"Erro ao decodificar o arquivo de cache: {self.cache_file}. Criando novo cache.")
            # Faz backup do arquivo corrompido
            if os.path.exists(self.cache_file):
                backup_file = f"{self.cache_file}.bak.{int(time.time())}"
                try:
                    os.rename(self.cache_file, backup_file)
                    print(f"Backup do cache corrompido criado em: {backup_file}")
                except Exception as e:
                    print(f"Não foi possível criar backup do cache corrompido: {str(e)}")
            return {}
    
    def save_cache(self, force=False):
        """
        Salva o cache no disco com proteção de mutex
        Se force=False, só salva se atingir o limite de alterações ou tempo
        """
        current_time = time.time()
        time_since_last_save = current_time - self.last_save
        
        # Salva apenas se for forçado, ou se atingir o limite de alterações, 
        # ou se passou tempo suficiente desde a última salvagem
        if not force and self.changes < self.save_interval and time_since_last_save < self.max_time_between_saves:
            return
            
        with self.mutex:
            # Primeiro salvamos em um arquivo temporário, depois fazemos o rename
            # para evitar corrupção em caso de falha durante a escrita
            temp_file = f"{self.cache_file}.temp"
            try:
                with open(temp_file, 'w', encoding='utf-8') as file:
                    json.dump(self.ids, file, indent=4, ensure_ascii=False)
                
                # Em sistemas Unix, rename é atômico
                if os.path.exists(temp_file):
                    os.replace(temp_file, self.cache_file)
                
                # Reseta o contador e atualiza o timestamp
                self.changes = 0
                self.last_save = current_time
            except Exception as e:
                print(f"Erro ao salvar cache: {str(e)}")
                # Tenta remover o arquivo temporário em caso de falha
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
    
    def get_id(self, name):
        """
        Obtém o ID do cache
        """
        return self.ids.get(name)
    
    def set_id(self, name, imdb_id):
        """
        Define o ID no cache e incrementa o contador de alterações
        """
        with self.mutex:
            self.ids[name] = imdb_id
            self.changes += 1
            
        # Tenta salvar o cache (só salvará se atingir o limite ou o tempo)
        self.save_cache()
    
    def has_id(self, name):
        """
        Verifica se o nome está no cache
        """
        return name in self.ids
        
    def __del__(self):
        """
        Garante que o cache seja salvo quando o objeto for destruído
        """
        try:
            self.save_cache(force=True)
        except:
            pass 