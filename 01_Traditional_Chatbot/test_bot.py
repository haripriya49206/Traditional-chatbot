"""Behavior checks including ambiguous input and the actual HTTP boundary."""
import json
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from bot import get_response
from app import Handler


class BotTests(unittest.TestCase):
    def test_supported_intents(self):
        for text, intent in [("hello", "greeting"), ("help", "help"), ("library hours", "library"), ("How do I apply?", "admissions"), ("tuition fees", "tuition"), ("forgot password", "it_support"), ("bye", "goodbye")]:
            with self.subTest(text=text):
                self.assertEqual(get_response(text)["intent"], intent)

    def test_case_and_whitespace(self):
        self.assertEqual(get_response("  LIBRARY   HOURS  ")["intent"], "library")

    def test_word_boundaries(self):
        self.assertEqual(get_response("this spaceship")["intent"], "fallback")

    def test_invalid_inputs(self):
        for value in ["", "   ", "???", None, 12, [], "x" * 501]:
            with self.subTest(value=value):
                self.assertEqual(get_response(value)["intent"], "invalid")

    def test_multiple_topics(self):
        self.assertEqual(get_response("library and tuition")["intent"], "clarify")

    def test_topic_over_greeting(self):
        self.assertEqual(get_response("Hi, what are library hours?")["intent"], "library")

    def test_help_priority(self):
        self.assertEqual(get_response("help with library")["intent"], "help")


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, data):
        return urlopen(Request(self.url + "/api/chat", data=data, headers={"Content-Type": "application/json"}), timeout=5)

    def test_page(self):
        with urlopen(self.url, timeout=5) as response:
            self.assertIn(b"Campus Help Bot", response.read())

    def test_chat(self):
        with self.post(b'{"message":"library"}') as response:
            self.assertEqual(json.load(response)["intent"], "library")

    def test_bad_payloads(self):
        for data in [b"not json", b"[]", b"\xff", b"", b"x" * 8193]:
            with self.subTest(data=data[:20]):
                with self.assertRaises(HTTPError) as error:
                    self.post(data)
                self.assertEqual(error.exception.code, 400)
                error.exception.close()

    def test_missing_message(self):
        with self.post(b'{}') as response:
            self.assertEqual(json.load(response)["intent"], "invalid")

    def test_missing_route(self):
        with self.assertRaises(HTTPError) as error:
            urlopen(self.url + "/missing", timeout=5)
        self.assertEqual(error.exception.code, 404)
        error.exception.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
