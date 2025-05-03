import json
import requests


group_entity_abbreviations = [
    "ООО",  # Общество с ограниченной ответственностью
    "ОАО",  # Открытое акционерное общество
    "ЗАО",  # Закрытое акционерное общество
    "ПАО",  # Публичное акционерное общество
    "ТСЖ",  # Товарищество собственников жилья
    "АО",   # Акционерное общество
    "СП",   # Совместное предприятие
    "ГП",   # Государственное предприятие
    "ТПК",  # Торгово-производственная компания
    "АУ",   # Автономное учреждение
    "МУП",  # Муниципальное унитарное предприятие
    "ГУП",  # Государственное унитарное предприятие
    "ПТ",   # Производственное товарищество
    "ПК",   # Производственный кооператив
    "СНТ",  # Садоводческое некоммерческое товарищество
    "ОП",   # Обособленное подразделение
]
try:
    f_path = open('abbreviations.json')
    path = 'abbreviations.json'
    f_path.close()
except FileNotFoundError:
    path = 'data/abbreviations.json'
with open(path, encoding='UTF-8') as f:
    all_abbreviations = json.load(f)


def change_if_full_comp(boss):
    for full in all_abbreviations.keys():
        if full.lower() in boss.lower():
            new = boss.lower().split(full.lower())
            new[0], new[1] = all_abbreviations[full], new[1].upper()
            return ''.join(new)
    return boss


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
            print(suggestion)
            boss_nsp = suggestion['data']['management']['name'] if suggestion['data'].get(
                'management') else suggestion['data']['name']['full']
            boss_nsp = change_if_full_comp(boss_nsp) if suggestion['data']['opf']['short'] in group_entity_abbreviations else boss_nsp

            return title, address, boss_nsp
        else:
            return "Не найдено", "Не найдено", "Не найдено"

    except Exception as e:
        print(f"Ошибка при запросе к Dadata API: {e}")
        return "Ошибка", "Ошибка", "Ошибка"
