#!/usr/bin/env python3
import argparse
import os
import sys
from config.settings import DEFAULT_INPUT_FILE, DEFAULT_OUTPUT_FILE
from src.parsers.m3u_parser import M3UParser
from src.utils.media_processor import MediaProcessor
from src.utils.json_exporter import JSONExporter

def main():
    # Configura os argumentos da linha de comando
    parser = argparse.ArgumentParser(description='Conversor de M3U para JSON com busca de IMDb IDs')
    parser.add_argument('-i', '--input', help='Arquivo M3U de entrada', default=DEFAULT_INPUT_FILE)
    parser.add_argument('-o', '--output', help='Arquivo JSON de saída', default=DEFAULT_OUTPUT_FILE)
    parser.add_argument('-v', '--verbose', help='Modo verboso com logs detalhados', action='store_true')
    parser.add_argument('-t', '--test', help='Modo de teste com exemplo específico', action='store_true')
    args = parser.parse_args()
    
    # Modo de teste para verificar as melhorias
    if args.test:
        run_test_mode(args.verbose)
        return
    
    # Verifica se o arquivo de entrada existe
    if not os.path.exists(args.input):
        print(f"Erro: O arquivo de entrada '{args.input}' não foi encontrado.")
        sys.exit(1)
    
    # Cria as instâncias das classes
    m3u_parser = M3UParser()
    media_processor = MediaProcessor(verbose=args.verbose)
    
    # Processa o arquivo M3U
    print(f"Analisando o arquivo M3U: {args.input}")
    entries = m3u_parser.parse_file(args.input)
    print(f"Encontradas {len(entries)} entradas para processar.")
    
    # Processa as entradas para buscar os IMDb IDs
    processed_entries = media_processor.process_entries(entries)
    
    # Exporta para JSON
    count = JSONExporter.export_to_file(processed_entries, args.output)
    
    print(f"\nProcessamento concluído! {count} entradas foram salvas em '{args.output}'.")

def run_test_mode(verbose):
    """
    Executa o modo de teste com exemplos específicos
    """
    from src.api.tmdb_client import TMDbClient
    from src.models.media_entry import MediaEntry
    
    # Exemplos problemáticos para testar
    test_cases = [
        ("Hotel Transylvania 1", False),
        ("Irmao Urso 1", False),
        ("O Reino Gelado 1", False),
        ("Shrek 1", False),
        ("Tarzan 1999", False),
        ("Hotel Transylvania", False),  # Para comparação
        ("Toy Story 3", False),  # Caso regular
    ]
    
    # Inicializa o cliente TMDb com modo verboso se especificado
    client = TMDbClient(verbose=verbose)
    
    print("Executando modo de teste com exemplos específicos:")
    print("-" * 50)
    
    for name, is_series in test_cases:
        print(f"\nTestando: '{name}'")
        imdb_id = client.get_imdb_id(name, is_series)
        if imdb_id:
            print(f"✅ Sucesso! IMDb ID encontrado: {imdb_id}")
        else:
            print(f"❌ Falha! IMDb ID não encontrado para: {name}")
    
    print("\nTeste concluído.")

if __name__ == "__main__":
    main() 