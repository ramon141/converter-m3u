import json

class JSONExporter:
    """
    Classe para exportar entradas para um arquivo JSON
    """
    @staticmethod
    def export_to_file(entries, file_path):
        """
        Exporta uma lista de entradas para um arquivo JSON
        """
        # Converte as entradas para dicionários
        json_entries = [entry.to_dict() for entry in entries]
        
        # Salva no arquivo
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(json_entries, file, indent=4, ensure_ascii=False)
            
        return len(json_entries) 