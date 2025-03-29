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
    args = parser.parse_args()
    
    # Verifica se o arquivo de entrada existe
    if not os.path.exists(args.input):
        print(f"Erro: O arquivo de entrada '{args.input}' não foi encontrado.")
        sys.exit(1)
    
    # Cria as instâncias das classes
    m3u_parser = M3UParser()
    media_processor = MediaProcessor()
    
    # Processa o arquivo M3U
    print(f"Analisando o arquivo M3U: {args.input}")
    entries = m3u_parser.parse_file(args.input)
    print(f"Encontradas {len(entries)} entradas para processar.")
    
    # Processa as entradas para buscar os IMDb IDs
    processed_entries = media_processor.process_entries(entries)
    
    # Exporta para JSON
    count = JSONExporter.export_to_file(processed_entries, args.output)
    
    print(f"\nProcessamento concluído! {count} entradas foram salvas em '{args.output}'.")

if __name__ == "__main__":
    main() 