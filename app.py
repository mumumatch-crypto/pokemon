"""寶可夢圖片探索站的 Flask 應用程式。"""

import random
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

POKEMON_API_URL = "https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
ALLOWED_IMAGE_HOSTS = {"raw.githubusercontent.com"}


def api_error(message: str, status_code: int):
    """以統一格式回傳 API 錯誤。"""
    return jsonify({"ok": False, "error": message}), status_code


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"ok": True})


@app.get("/api/pokemon")
def pokemon():
    pokemon_id = random.randint(1, 1025)
    try:
        response = requests.get(POKEMON_API_URL.format(pokemon_id=pokemon_id), timeout=5)
    except requests.exceptions.Timeout:
        return api_error("連線至 PokéAPI 逾時，請稍後再試。", 504)
    except requests.exceptions.RequestException:
        return api_error("無法連線至 PokéAPI，請稍後再試。", 502)

    if response.status_code == 429:
        return api_error("PokéAPI 請求過於頻繁，請稍後再試。", 429)
    if response.status_code != 200:
        return api_error("PokéAPI 回傳非預期狀態，請稍後再試。", 502)

    try:
        data = response.json()
    except ValueError:
        return api_error("PokéAPI 回應不是有效的 JSON。", 502)

    if not isinstance(data, dict):
        return api_error("PokéAPI 回應缺少寶可夢資料。", 502)
    sprites = data.get("sprites")
    if not isinstance(sprites, dict):
        return api_error("PokéAPI 回應缺少 sprites 欄位。", 502)

    artwork = sprites.get("other")
    artwork = artwork.get("official-artwork") if isinstance(artwork, dict) else None
    image_url = artwork.get("front_default") if isinstance(artwork, dict) else None
    if not image_url:
        image_url = sprites.get("front_default")
    if not isinstance(image_url, str) or not image_url:
        return api_error("PokéAPI 回應缺少圖片欄位。", 502)

    parsed_url = urlparse(image_url)
    if parsed_url.scheme != "https" or parsed_url.hostname not in ALLOWED_IMAGE_HOSTS:
        return api_error("PokéAPI 圖片網址未通過安全驗證。", 502)

    name = data.get("name")
    if not isinstance(name, str) or not name:
        return api_error("PokéAPI 回應缺少寶可夢名稱。", 502)

    return jsonify({
        "ok": True,
        "image_url": image_url,
        "source": "pokemon",
        "pokemon_id": pokemon_id,
        "pokemon_name": name,
    })


if __name__ == "__main__":
    app.run()
