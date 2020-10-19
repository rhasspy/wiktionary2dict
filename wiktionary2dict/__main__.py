#!/usr/bin/env python3
"""Command-line utility for extracting IPA pronunciations from a Wiktionary XML dump."""
import argparse
import logging
import os
import sys

from . import (
    process_cs,
    process_en_us,
    process_fr,
    process_it,
    process_nld,
    wiktionary2dict,
)

_LOGGER = logging.getLogger("wiktionary2dict")

_LANG_PROCESS = {
    "en-us": process_en_us,
    "nl-nl": process_nld,
    "cs-cz": process_cs,
    "it-it": process_it,
    "fr-fr": process_fr,
}

# -----------------------------------------------------------------------------


def main():
    """Main entry point"""
    args = get_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    _LOGGER.debug(args)

    casing = None
    if args.casing == "lower":
        casing = str.lower
    elif args.casing == "upper":
        casing = str.upper

    process_func = _LANG_PROCESS.get(args.language)
    assert process_func, f"No wiktionary processor for code {args.language}"

    if os.isatty(sys.stdin.fileno()):
        print("Reading XML from stdin...", file=sys.stderr)

    # Process XML and write lexicon to stdout
    pron_generator = wiktionary2dict(sys.stdin.buffer, process_func)
    for word, word_pron in pron_generator:
        if casing:
            word = casing(word)

        print(word, word_pron, sep=args.word_separator)


# -----------------------------------------------------------------------------


def get_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="wiktionary2dict",
        description="Extract IPA pronunciations from Wiktionary XML dump",
    )
    parser.add_argument(
        "language", choices=sorted(_LANG_PROCESS.keys()), help="Language code"
    )
    parser.add_argument(
        "--casing",
        choices=["lower", "upper", "ignore"],
        default="ignore",
        help="Case transformation to apply to words",
    )
    parser.add_argument(
        "--word-separator",
        default=" ",
        help="Separator between a word and its pronunciation in output (default: space)",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG log to console"
    )

    return parser.parse_args()


# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
