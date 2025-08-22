import json
import unittest
from hijiki.builders.message_builder import MessageBuilder
from hijiki.models.message_cover import MessageCover


class TestMessageBuilder(unittest.TestCase):
    def setUp(self):
        self.payload = {"id": 1, "nome": "Teste"}

    def test_message_builder_basic(self):
        mensagem_json = (
            MessageBuilder()
            .with_version("v1")
            .with_value(self.payload)
            .build()
        )

        data = json.loads(mensagem_json)
        self.assertEqual(data["version"], "v1")
        self.assertEqual(data["value"], self.payload)
        self.assertNotIn("context", data)
        self.assertNotIn("extra_data", data)

    def test_message_builder_with_all_fields(self):
        payload = {"id": 42}
        extra_data = {"debug": True}
        mensagem_json = (
            MessageBuilder()
            .with_version("v2")
            .with_value(payload)
            .with_context("processamento")
            .with_extra_data(extra_data)
            .build()
        )

        data = json.loads(mensagem_json)
        self.assertEqual(data["version"], "v2")
        self.assertEqual(data["value"], payload)
        self.assertEqual(data["context"], "processamento")
        self.assertEqual(data["extra_data"], extra_data)

    def test_message_builder_missing_required_fields(self):
        builder = MessageBuilder()
        with self.assertRaises(ValueError) as context:
            builder.build()
        self.assertIn("versão e o valor", str(context.exception))

    def test_message_cover_to_json(self):
        cover = MessageCover(
            version="v1",
            value=self.payload,
            context="ctx",
            extra_data={"debug": True}
        )
        data = json.loads(cover.to_json())
        self.assertEqual(data["version"], "v1")
        self.assertEqual(data["value"], self.payload)
        self.assertEqual(data["context"], "ctx")
        self.assertEqual(data["extra_data"], {"debug": True})
