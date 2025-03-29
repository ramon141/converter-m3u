class MediaEntry:
    """
    Classe que representa uma entrada de mídia (filme ou série)
    """
    def __init__(self, name, url, language="portuguese", group_title=""):
        self.name = name
        self.url = url
        self.language = language
        self.group_title = group_title
        self.imdb_id = None
        self.season = None
        self.episode = None
        self.is_series = False
        
    def set_imdb_id(self, imdb_id):
        """
        Define o IMDb ID da entrada
        """
        self.imdb_id = imdb_id
        return self
        
    def set_series_info(self, season, episode):
        """
        Define as informações de temporada e episódio para séries
        """
        self.season = season
        self.episode = episode
        self.is_series = True if season is not None and episode is not None else False
        return self
        
    def to_dict(self):
        """
        Converte a entrada para um dicionário
        """
        result = {
            "name": self.name,
            "url": self.url,
            "language": self.language
        }
        
        if self.imdb_id:
            result["imdb_id"] = self.imdb_id
            
        if self.is_series:
            result["season"] = self.season
            result["episode"] = self.episode
            
        return result 