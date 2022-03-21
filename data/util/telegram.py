import requests


def send_message(message, key):
    """
    Send a message to a telegram bot.
    """

    url = "https://api.telegram.org/bot{}/sendMessage".format(key)
    payload = {"chat_id": "653083546", "text": message}
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass
