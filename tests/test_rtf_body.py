#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tests for compressed-RTF body handling in MsOxMessage._rtf_compressed_to_text."""

import unittest
from unittest import mock

import compressed_rtf

from msg_parser.msg_parser import MsOxMessage


class TestRtfCompressedToText(unittest.TestCase):
    """RTF-only message bodies must decode to text without taking down the parse."""

    def test_empty_rtf_shell_collapses_to_empty_string(self):
        """An RTF formatting shell with no real text yields '' (so callers can
        treat it as a body-less message), not raw RTF markup."""
        shell = (
            rb"{\rtf1\ansi\deff0{\fonttbl{\f0\fswiss Arial;}}"
            rb"{\colortbl\red0\green0\blue0;}\f0\fs20 }"
        )
        body = MsOxMessage._rtf_compressed_to_text(compressed_rtf.compress(shell))
        self.assertIsInstance(body, str)
        self.assertEqual(body.strip(), "")

    def test_real_rtf_text_is_extracted_as_string(self):
        """An RTF body with real text comes back as that plain text (a str),
        never as raw bytes of RTF markup."""
        doc = rb"{\rtf1\ansi\deff0{\fonttbl{\f0\fswiss Arial;}}\f0\fs20 Hello world.}"
        body = MsOxMessage._rtf_compressed_to_text(compressed_rtf.compress(doc))
        self.assertIsInstance(body, str)
        self.assertIn("Hello world.", body)

    def test_striprtf_runtime_error_falls_back_to_decoded_rtf(self):
        """If striprtf raises at runtime, keep the decoded RTF rather than
        aborting the parse and losing already-readable headers/attachments."""
        compressed = compressed_rtf.compress(rb"{\rtf1\ansi\deff0 hello}")
        with mock.patch("striprtf.striprtf.rtf_to_text", side_effect=ValueError("boom")):
            body = MsOxMessage._rtf_compressed_to_text(compressed)
        self.assertIsInstance(body, str)
        self.assertIn("rtf1", body)  # decoded RTF preserved, no exception raised

    def test_corrupt_stream_still_raises(self):
        """A genuinely unsupported/corrupt compressed stream must surface rather
        than be silently swallowed, so callers can flag broken files."""
        with self.assertRaises(Exception):
            MsOxMessage._rtf_compressed_to_text(b"not a valid compressed rtf stream")


if __name__ == "__main__":
    unittest.main()
