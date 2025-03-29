import json
import sys
import os

def load_json_array(file_path):
    """
    Carrega um arquivo JSON e retorna seu conteúdo como uma lista.
    Verifica se o JSON é um array.
    """
    if not os.path.exists(file_path):
        print(f"Erro: O arquivo '{file_path}' não existe.")
        sys.exit(1)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if not isinstance(data, list):
                print(f"Erro: O arquivo '{file_path}' não contém um array JSON.")
                sys.exit(1)
            print(f"Arquivo '{file_path}' carregado com sucesso. Contém {len(data)} elementos.")
            return data
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar o JSON no arquivo '{file_path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao ler o arquivo '{file_path}': {e}")
        sys.exit(1)

def merge_json_arrays(json_array1, json_array2):
    """
    Mescla duas listas JSON.
    """
    merged = json_array1 + json_array2
    print(f"Arrays mesclados com sucesso. Total de elementos: {len(merged)}.")
    return merged

def save_json_array(data, output_path):
    """
    Salva uma lista como um arquivo JSON.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Arquivo mesclado salvo como '{output_path}'.")
    except Exception as e:
        print(f"Erro ao escrever no arquivo '{output_path}': {e}")
        sys.exit(1)

def main():
    # Caminhos dos arquivos
    file1 = 'output_first.json'
    file2 = 'output.json'
    output_file = 'all.json'

    # Carregar os arquivos JSON
    json_array1 = load_json_array(file1)
    json_array2 = load_json_array(file2)

    # Mesclar os arrays JSON
    merged_json_array = merge_json_arrays(json_array1, json_array2)

    # Salvar o array JSON mesclado
    save_json_array(merged_json_array, output_file)

if __name__ == "__main__":
    main()
