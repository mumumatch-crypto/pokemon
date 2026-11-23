import unittest
from unittest.mock import patch

import requests

import app as app_module


IMAGE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"


def pokemon_payload(image_url=IMAGE_URL):
    return {
        "name": "pikachu",
        "sprites": {
            "other": {"official-artwork": {"front_default": image_url}},
            "front_default": image_url,
        },
    }


class PokemonAppTests(unittest.TestCase):
    def setUp(self):
        app_module.app.config.update(TESTING=True)
        self.client = app_module.app.test_client()

    def mocked_response(self, status=200, payload=None):
        response = unittest.mock.Mock()
        response.status_code = status
        response.json.return_value = payload if payload is not None else pokemon_payload()
        return response

    def test_homepage_returns_200_and_title(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("寶可夢圖片探索站".encode(), response.data)
        self.assertIn(b"https://pokeapi.co/docs/v2", response.data)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"ok": True})

    @patch("app.random.randint", return_value=25)
    @patch("app.requests.get")
    def test_pokemon_success(self, get, randint):
        get.return_value = self.mocked_response()
        response = self.client.get("/api/pokemon")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "ok": True, "image_url": IMAGE_URL, "source": "pokemon",
            "pokemon_id": 25, "pokemon_name": "pikachu",
        })
        get.assert_called_once_with("https://pokeapi.co/api/v2/pokemon/25", timeout=5)

    @patch("app.requests.get")
    def test_upstream_429(self, get):
        get.return_value = self.mocked_response(status=429)
        response = self.client.get("/api/pokemon")
        self.assertEqual(response.status_code, 429)
        self.assertFalse(response.get_json()["ok"])

    @patch("app.requests.get", side_effect=requests.exceptions.Timeout)
    def test_timeout(self, get):
        response = self.client.get("/api/pokemon")
        self.assertEqual(response.status_code, 504)
        self.assertFalse(response.get_json()["ok"])

    @patch("app.requests.get")
    def test_invalid_json(self, get):
        upstream = self.mocked_response()
        upstream.json.side_effect = ValueError("invalid json")
        get.return_value = upstream
        response = self.client.get("/api/pokemon")
        self.assertEqual(response.status_code, 502)
        self.assertFalse(response.get_json()["ok"])

    @patch("app.requests.get")
    def test_missing_sprites(self, get):
        get.return_value = self.mocked_response(payload={"name": "pikachu"})
        response = self.client.get("/api/pokemon")
        self.assertEqual(response.status_code, 502)
        self.assertFalse(response.get_json()["ok"])

    @patch("app.requests.get")
    def test_rejects_non_https_image_url(self, get):
        get.return_value = self.mocked_response(payload=pokemon_payload(IMAGE_URL.replace("https://", "http://")))
        response = self.client.get("/api/pokemon")
        self.assertEqual(response.status_code, 502)
        self.assertFalse(response.get_json()["ok"])

    @patch("app.requests.get")
    def test_rejects_non_allowlisted_image_host(self, get):
        get.return_value = self.mocked_response(payload=pokemon_payload("https://example.com/pikachu.png"))
        response = self.client.get("/api/pokemon")
        self.assertEqual(response.status_code, 502)
        self.assertFalse(response.get_json()["ok"])

    @patch("app.requests.get")
    def test_upstream_non_200(self, get):
        get.return_value = self.mocked_response(status=503)
        response = self.client.get("/api/pokemon")
        self.assertEqual(response.status_code, 502)
        self.assertFalse(response.get_json()["ok"])

    @patch("app.requests.get", side_effect=requests.exceptions.ConnectionError)
    def test_connection_error(self, get):
        response = self.client.get("/api/pokemon")
        self.assertEqual(response.status_code, 502)
        self.assertFalse(response.get_json()["ok"])

    @patch("app.requests.get")
    def test_missing_image_url(self, get):
        get.return_value = self.mocked_response(payload={"name": "pikachu", "sprites": {"other": {}}})
        response = self.client.get("/api/pokemon")
        self.assertEqual(response.status_code, 502)
        self.assertFalse(response.get_json()["ok"])


if __name__ == "__main__":
    unittest.main()
