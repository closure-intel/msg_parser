#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tests for EmailFormatter body handling."""

import unittest

from msg_parser.email_builder import EmailFormatter


class _FakeAttachment:
    AttachMimeTag = "application/pdf"
    data = b"%PDF-1.4 fake attachment bytes"
    Filename = "evidence.pdf"


class _FakeMsg:
    """Minimal stand-in exposing the attributes EmailFormatter.build_email reads."""

    def __init__(self, body):
        self.message_id = "<id@example.com>"
        self.subject = "subject only message"
        self.sent_date = "Mon, 13 Jan 2025 10:54:13 -0800"
        self.sender = ["sender@example.com"]
        self.reply_to = None
        self.header_dict = {}
        self.body = body
        self.attachments = [_FakeAttachment()]


class TestEmptyBodyExport(unittest.TestCase):
    """Body-less messages must still export instead of dropping the whole file."""

    def test_empty_body_still_builds_with_attachments(self):
        """A subject-only / RTF-shell message (empty or missing body) must build
        an EML with its attachments intact, not raise KeyError."""
        for empty_body in ("", None):
            eml = EmailFormatter(_FakeMsg(empty_body)).build_email()
            self.assertIsInstance(eml, str)
            # an (empty) body part is attached rather than raising
            self.assertIn("Content-Type: text/plain", eml)
            # and the attachment survives
            self.assertIn("Content-Disposition: attachment", eml)
            self.assertIn("evidence.pdf", eml)


if __name__ == "__main__":
    unittest.main()
