import re
from src.models.media_entry import MediaEntry
from src.utils.text_cleaner import TextCleaner

class M3UParser:
    """
    Classe para analisar arquivos M3U e convertê-los em objetos MediaEntry
    """
    def __init__(self):
        self.text_cleaner = TextCleaner()
    
    def parse_file(self, file_path):
        """
        Analisa um arquivo M3U e retorna uma lista de objetos MediaEntry
        """
        entries = []
        
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        for i, line in enumerate(lines):
            if line.startswith("#EXTINF"):
                # Extrai informações da linha
                match_group_title = re.search(r'group-title="([^"]+)"', line)
                group_title = match_group_title.group(1) if match_group_title else ""
                
                # Ignora canais de TV
                if group_title.startswith("Canais"):
                    continue
                
                match_name = re.search(r'tvg-name="([^"]+)"', line)
                if match_name and i + 1 < len(lines):
                    name = match_name.group(1).strip()
                    url = lines[i + 1].strip()
                    
                    # Verifica se a URL é válida
                    if not url.startswith("http"):
                        print(f"URL inválida encontrada: {url}. Ignorando entrada.")
                        continue
                    
                    # Detecta o idioma
                    language = TextCleaner.detect_language(name, group_title)
                    
                    # Cria a entrada
                    entry = MediaEntry(name, url, language, group_title)
                    
                    # Limpa o nome e extrai informações de série, se for o caso
                    series_name, season, episode = TextCleaner.extract_series_info(name)
                    
                    # Se for uma série, atualiza o nome e adiciona informações de temporada e episódio
                    if season is not None and episode is not None:
                        entry.name = series_name
                        entry.set_series_info(season, episode)
                    else:
                        entry.name = TextCleaner.clean_name(name)
                    
                    entries.append(entry)
        
        return entries 