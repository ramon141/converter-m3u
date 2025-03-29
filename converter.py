import requests
import re
import json
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# Substitua pelas suas credenciais
API_KEY = '9572ac540e32170048c25aaa5bb93fb9'  # Chave de API do TMDb
BEARER_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5NTcyYWM1NDBlMzIxNzAwNDhjMjVhYWE1YmI5M2ZiOSIsIm5iZiI6MTczMTcxMDQyNC4wMzczNDQ3LCJzdWIiOiI1ZWNiY2UwODE0MGJhZDAwMWIxZjkyZGUiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.ZN9Z5nN2ppedCBvqxj8-Cp-7L-hctLzYReE_nOQSFEY'  # Token de Bearer do TMDb
CACHE_FILE = "cache_ids.json"

# Carrega o cache do disco
def load_cache():
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Salva o cache no disco
def save_cache(cache):
    with open(CACHE_FILE, 'w', encoding='utf-8') as file:
        json.dump(cache, file, indent=4, ensure_ascii=False)

ids = load_cache()

def make_request_with_retry(url, params=None, headers=None, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 30))
            print(f"\nRecebeu erro 429. Esperando {retry_after} segundos antes de tentar novamente...")
            time.sleep(retry_after)
            attempt += 1
        else:
            return response
    print(f"\nMáximo de tentativas alcançado para a URL: {url}")
    return None

def get_imdb_id(name, is_series=False):
    if name in ids:
        return ids[name]

    search_url = f"https://api.themoviedb.org/3/search/{'tv' if is_series else 'movie'}"
    search_params = {"api_key": API_KEY, "query": name, "language": "pt-br"}
    search_response = make_request_with_retry(search_url, params=search_params)

    if search_response and search_response.status_code == 200:
        results = search_response.json().get("results", [])
        if results:
            tmdb_id = results[0]["id"]
            external_ids_url = f"https://api.themoviedb.org/3/{'tv' if is_series else 'movie'}/{tmdb_id}/external_ids"
            headers = {
                "Authorization": f"Bearer {BEARER_TOKEN}",
                "accept": "application/json"
            }
            external_ids_response = make_request_with_retry(external_ids_url, headers=headers)
            if external_ids_response and external_ids_response.status_code == 200:
                external_ids = external_ids_response.json()
                imdb_id = external_ids.get("imdb_id")
                ids[name] = imdb_id  # Atualiza o cache
                return imdb_id
            else:
                print(f"Não tem o IMDb ID para: {name}")
        else:
            print(f"IMDb ID não encontrado para: {name}")        
    print(f"IMDb ID não encontrado para: {name}")
    return None

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

def extract_series_info(name):
    """
    Extrai informações da série: nome, temporada e episódio.
    """
    match = re.search(r'[Ss](\d+)[Ee](\d+)', name)
    if match:
        season = int(match.group(1))
        episode = int(match.group(2))
        series_name = re.sub(r'[Ss]\d+[Ee]\d+', '', name).strip()
        series_name = clean_name(series_name)  # Limpa o nome da série
        return series_name, season, episode
    return clean_name(name), None, None

def fetch_imdb_id(entry):
    """
    Processa uma entrada para buscar o IMDb ID.
    """
    is_series = False
    series_name, season, episode = extract_series_info(entry["name"])
    if season is not None and episode is not None:
        is_series = True
        name = series_name
    else:
        name = clean_name(entry["name"])

    imdb_id = get_imdb_id(name, is_series)
    if imdb_id:
        entry["imdb_id"] = imdb_id
        if is_series:
            entry["season"] = season
            entry["episode"] = episode
        return entry
    return None

def parse_m3u_to_json(input_file):
    json_output = []
    entries = []
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            match_group_title = re.search(r'group-title="([^"]+)"', line)
            group_title = match_group_title.group(1) if match_group_title else ""

            if group_title.startswith("Canais"):
                continue

            match_name = re.search(r'tvg-name="([^"]+)"', line)
            if match_name:
                name = match_name.group(1).strip()
                url = lines[i + 1].strip()

                if not url.startswith("http"):
                    print(f"URL inválida encontrada: {url}. Ignorando entrada.")
                    continue

                # Detecta se é legendado
                language = "portuguese"
                if "[L]" in name or "(L)" in name or "Legendado" in group_title:
                    language = "legendado"
                    name = clean_name(name)  # Remove o "[L]" ou "(L)"

                entry = {
                    "name": name,
                    "url": url,
                    "language": language,
                }
                entries.append(entry)

    # Processa as entradas em paralelo
    with ThreadPoolExecutor(max_workers=5) as executor:
        for result in tqdm(executor.map(fetch_imdb_id, entries), total=len(entries), desc="Consultando TMDb"):
            if result:
                json_output.append(result)

    return json_output

def main():
    input_m3u = "input.m3u"
    output_json_file = "output.json"

    json_result = parse_m3u_to_json(input_m3u)

    with open(output_json_file, 'w', encoding='utf-8') as file:
        json.dump(json_result, file, indent=4, ensure_ascii=False)

    save_cache(ids)  # Salva o cache atualizado
    print(f"\nProcessamento concluído! {len(json_result)} entradas foram salvas em '{output_json_file}'.")

if __name__ == "__main__":
    main()
