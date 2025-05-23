import requests
import json
from .config import SMARTCAPTCHA_SERVER_KEY


# функция, проверяющая корректность введённой капчи с помощью серверов яндекса
def check_captcha(app, token, ip):
    resp = requests.post(
        "https://smartcaptcha.yandexcloud.net/validate",
        data={
            "secret": SMARTCAPTCHA_SERVER_KEY,
            "token": token,
            "ip": ip
        },
        timeout=1
    )
    server_output = resp.content.decode()
    if resp.status_code != 200:
        app.logger.error(f"Allow access due to an error: code={resp.status_code}; message={server_output}")
        return True
    return json.loads(server_output)["status"] == "ok"
