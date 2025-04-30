import requests


def get_info_by_inn(inn):
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"
    token = "d7a26c02b1fcfcc8aae5223ef09ae3737377dccb"
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }
    data = {
        "query": inn
    }
    try:
        response = requests.post(url, json=data, headers=headers, timeout=5)
        response.raise_for_status()
        result = response.json()

        if result.get('suggestions'):
            suggestion = result['suggestions'][0]
            title = suggestion['value']
            address = suggestion['data']['address']['value']
            boss_nsp = suggestion['data']['management']['name'] if suggestion['data'].get(
                'management') else "Не найдено"
            return title, address, boss_nsp
        else:
            return "Не найдено", "Не найдено", "Не найдено"

    except Exception as e:
        print(f"Ошибка при запросе к Dadata API: {e}")
        return "Ошибка", "Ошибка", "Ошибка"