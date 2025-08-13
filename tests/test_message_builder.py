import json
import unittest
from unittest.mock import patch
from hijiki.builders.message_builder import MessageBuilder
from hijiki.models.message_cover import MessageCover


class TestMessageBuilder(unittest.TestCase):
    def setUp(self):
        self.payload = {"id": 1, "nome": "Teste"}

    def test_message_builder_old_format(self):
        def json_with_nulls(self, *args, **kwargs):
            return json.dumps({
                "version": self.version,
                "value": self.value,
                "context": self.context,
                "extra_data": self.extra_data
            })

        with patch.object(MessageCover, "json", json_with_nulls):
            mensagem_json = (
                MessageBuilder()
                .with_version("v1")
                .with_value(self.payload)
                .build()
            )

        data = json.loads(mensagem_json)
        self.assertEqual(data["version"], "v1")
        self.assertEqual(data["value"], self.payload)

    def test_message_builder_new_format_excludes_none(self):
        payload = {"id": 1, "nome": "Teste"}
        mensagem_json = (
            MessageBuilder()
            .with_version("v1")
            .with_value(payload)
            .build()
        )

        data = json.loads(mensagem_json)
        assert data["version"] == "v1"
        assert data["value"] == payload
        assert "context" not in data
        assert "extra_data" not in data

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
        assert data["version"] == "v2"
        assert data["value"] == payload
        assert data["context"] == "processamento"
        assert data["extra_data"] == extra_data

    def test_message_builder_missing_required_fields(self):
        builder = MessageBuilder()
        with self.assertRaises(ValueError) as context:
            builder.build()
        self.assertIn("versão e o valor", str(context.exception))
