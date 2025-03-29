import re

class TextCleaner:
    """
    Classe para limpar e processar textos de nomes de filmes e séries
    """
    
    @staticmethod
    def clean_name(name):
        """
        Limpa o nome do filme ou série.
        - Remove tags como "[L]" e "(L)".
        - Remove anos no formato " - 2018", "(2019)".
        """
        name = re.sub(r'\[[Ll]\]', '', name)  # Remove tags como "[L]"
        name = re.sub(r'\(\s?[Ll]\s?\)', '', name)  # Remove "(L)" para legendado
        name = re.sub(r'-\s?\d{4}$', '', name)  # Remove o ano no final do nome
        name = re.sub(r'\(\d{4}\)', '', name).strip()  # Remove o ano entre parênteses
        return name.strip()
    
    @staticmethod
    def extract_series_info(name):
        """
        Extrai informações da série: nome, temporada e episódio.
        Retorna uma tupla (nome_da_série, temporada, episódio).
        Se não for uma série, retorna (nome_limpo, None, None).
        """
        match = re.search(r'[Ss](\d+)[Ee](\d+)', name)
        if match:
            season = int(match.group(1))
            episode = int(match.group(2))
            series_name = re.sub(r'[Ss]\d+[Ee]\d+', '', name).strip()
            series_name = TextCleaner.clean_name(series_name)  # Limpa o nome da série
            return series_name, season, episode
        return TextCleaner.clean_name(name), None, None
    
    @staticmethod
    def detect_language(name, group_title=""):
        """
        Detecta o idioma do conteúdo com base no nome e grupo.
        Retorna "legendado" se for legendado, caso contrário "portuguese".
        """
        if "[L]" in name or "(L)" in name or "Legendado" in group_title:
            return "legendado"
        return "portuguese" 