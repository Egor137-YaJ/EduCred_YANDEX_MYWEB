import requests
import json
from .config import SMARTCAPTCHA_SERVER_KEY


def check_captcha(app, token, ip):
    resp = requests.post(
        "https://smartcaptcha.yandexcloud.net/validate",
        data={
            "secret": SMARTCAPTCHA_SERVER_KEY,
            "token": token,
            "ip": ip  # Способ получения IP-адреса зависит от вашего фреймворка и прокси.
            # Например, во Flask это может быть request.remote_addr
        },
        timeout=1
    )
    server_output = resp.content.decode()
    if resp.status_code != 200:
        app.logger.error(f"Allow access due to an error: code={resp.status_code}; message={server_output}")
        return True
    return json.loads(server_output)["status"] == "ok"
