"""Methods for extracting IPA pronunciations from a Wiktionary XML dump."""
import re
import typing
import unicodedata
from collections import defaultdict

import lxml.etree as ElementTree

WORD_PRON_TYPE = typing.Tuple[str, str]

_NAMESPACE = "{http://www.mediawiki.org/xml/export-0.10/}"

# Digraph normalization
_DIGRAPHS = {"ʣ": "dz", "ʤ": "dʒ", "ʦ": "ts", "ʧ": "tʃ"}

# Primary/secondary stress markers
IPA_STRESS = {"ˈ", "ˌ"}

# -----------------------------------------------------------------------------


def wiktionary2dict(
    xml_file: typing.BinaryIO,
    process_func: typing.Callable[[str], typing.Iterable[str]],
) -> typing.Iterable[WORD_PRON_TYPE]:
    """
    Extract IPA pronunciations from wiktionary dump.

    Yields word, pronunciation tuples.
    """
    # Iterate over <page> elements
    for _, elem in ElementTree.iterparse(
        xml_file, tag=f"{_NAMESPACE}page", events=("end",)
    ):
        try:
            # <title>headword</title>
            word = elem.find(f"./{_NAMESPACE}title").text.strip()

            # <revision><text>...</text></revision>
            text = elem.find(f"./{_NAMESPACE}revision/{_NAMESPACE}text").text

            if (not word) or (not text):
                continue

            if (" " in word) or ("," in word):
                # Skip multi-words
                continue

            # <text> contains lines from wiktionary entry.
            # Do language-specific processing of text
            for word_pron in process_func(text):
                yield word, word_pron
        finally:
            # See: https://stackoverflow.com/questions/12160418/why-is-lxml-etree-iterparse-eating-up-all-my-memory
            # It's safe to call clear() here because no descendants will be
            # accessed
            elem.clear()
            # Also eliminate now-empty references from the root node to elem
            for ancestor in elem.xpath("ancestor-or-self::*"):
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]


# -----------------------------------------------------------------------------
# U.S. English
# -----------------------------------------------------------------------------

_EN_PRON_PATTERN = re.compile(r".+{{IPA\|en\|([^}]+)}}")
_EN_REGION_PRON_PATTERN = re.compile(r".+{{a\|([^}]+)}}\s+{{IPA\|en\|([^}]+)}}")


def process_en_us(text: str) -> typing.Iterable[str]:
    """Process U.S. English pronunciations"""
    # Look for IPA pronunciations in ==English== ===Pronunciation=== section.
    in_english = False
    in_pron = False
    done_with_text = False

    current_prons: typing.Dict[str, typing.List[str]] = defaultdict(list)

    for line in text.splitlines():
        if done_with_text:
            break

        line = line.strip()

        if in_english and in_pron:
            if line.startswith("==="):
                # New section
                done_with_text = True

                if current_prons:
                    us_prons = None
                    ga_prons = None
                    uk_prons = None
                    rp_prons = None

                    for region, prons in current_prons.items():
                        if "US" in region:
                            us_prons = prons
                        elif "UK" in region:
                            uk_prons = prons
                        elif ("GA" in region) or ("GenAm" in region):
                            ga_prons = prons
                        elif "RP" in region:
                            rp_prons = prons

                    best_prons = us_prons or ga_prons or uk_prons or rp_prons or []
                    for best_pron in best_prons:
                        yield best_pron

                    current_prons.clear()

                break

            pron_found = False

            # Look for an "IPA" pronunciation first
            for ipa_prons in _EN_PRON_PATTERN.findall(line):
                for ipa_pron in ipa_prons.split("|"):
                    if "xxx" in ipa_pron:
                        continue

                    ipa_pron = _refine_pron(ipa_pron)

                    if ipa_pron:
                        yield ipa_pron
                        pron_found = True

            if not pron_found:
                # Try to find a region-specific pronunciation
                for region, ipa_prons in _EN_REGION_PRON_PATTERN.findall(line):
                    for ipa_pron in ipa_prons.split("|"):
                        if "xxx" in ipa_pron:
                            continue

                        ipa_pron = _refine_pron(ipa_pron)

                        if ipa_pron:
                            current_prons[region].append(ipa_pron)

        elif in_english and (line == "===Pronunciation==="):
            in_pron = True
        elif line == "==English==":
            in_english = True


# -----------------------------------------------------------------------------
# Dutch
# -----------------------------------------------------------------------------

_NLD_PRON_PATTERN = re.compile(r"IPA[^|]*\|/?([^/}]+)")


def process_nld(text: str) -> typing.Iterable[str]:
    """Process Nederlands Dutch pronunciations"""
    # Look for IPA pronunciations in =nld= -pron- section.
    in_nld = False
    in_pron = False
    done_with_text = False

    for line in text.splitlines():
        if done_with_text:
            break

        line = line.strip()

        if in_nld and in_pron:
            if line.startswith("{{=") or line.startswith("{{-"):
                # New section
                done_with_text = True
                break

            for ipa_pron in _NLD_PRON_PATTERN.findall(line):
                if "xxx" in ipa_pron:
                    continue

                ipa_pron = ipa_pron.replace("|nld", "")
                ipa_pron = _refine_pron(ipa_pron)

                if ipa_pron:
                    yield ipa_pron
        elif in_nld and (line == "{{-pron-}}"):
            in_pron = True
        elif line == "{{=nld=}}":
            in_nld = True


# -----------------------------------------------------------------------------
# Czech
# -----------------------------------------------------------------------------

_CS_PRON_PATTERN = re.compile(r"IPA[^|]*\|/?([^/}]+)")


def process_cs(text: str) -> typing.Iterable[str]:
    """Process Czech pronunciations"""
    # Look for IPA pronunciations in čeština (Czech) > výslovnost (pronuncation) section.
    in_czech = False
    in_pron = False
    done_with_text = False

    for line in text.splitlines():
        if done_with_text:
            break

        line = line.strip()

        if in_czech and in_pron:
            if line.startswith("="):
                # New section
                done_with_text = True
                break

            for ipa_pron in _CS_PRON_PATTERN.findall(line):
                ipa_pron = ipa_pron.lower()
                ipa_pron = _refine_pron(ipa_pron)

                if ipa_pron:
                    yield ipa_pron
        elif in_czech and (line == "=== výslovnost ==="):
            in_pron = True
        elif line == "== čeština ==":
            in_czech = True


# -----------------------------------------------------------------------------
# Italian
# -----------------------------------------------------------------------------

_IT_PRON_PATTERN = re.compile(r"IPA[^|]*\|/?([^/}]+)")


def process_it(text: str) -> typing.Iterable[str]:
    """Process Italian pronunciations"""
    # Look for IPA pronunciations in -it- > -pron- section.
    in_italian = False
    in_pron = False
    done_with_text = False

    for line in text.splitlines():
        if done_with_text:
            break

        line = line.strip()

        if in_italian and in_pron:
            if line.startswith("{{=") or line.startswith("{{-"):
                # New section
                done_with_text = True
                break

            for ipa_pron in _IT_PRON_PATTERN.findall(line):
                ipa_pron = ipa_pron.lower()
                ipa_pron = _refine_pron(ipa_pron)

                if ipa_pron:
                    yield ipa_pron
        elif in_italian and (line == "{{-pron-}}"):
            in_pron = True
        elif line == "== {{-it-}} ==":
            in_italian = True


# -----------------------------------------------------------------------------
# French
# -----------------------------------------------------------------------------

_FR_PRON_PATTERN = re.compile(r"{{pron\|([^\|]+)\|")


def process_fr(text: str) -> typing.Iterable[str]:
    """Process French pronunciations"""
    # Look for IPA pronunciations in langue|fr section.
    in_french = False
    done_with_text = False

    for line in text.splitlines():
        if done_with_text:
            break

        line = line.strip()

        if in_french:
            if line.startswith("== "):
                # New section
                done_with_text = True
                break

            for ipa_pron in _FR_PRON_PATTERN.findall(line):
                ipa_pron = ipa_pron.lower()
                ipa_pron = _refine_pron(ipa_pron)

                if ipa_pron:
                    yield ipa_pron
        elif line == "== {{langue|fr}} ==":
            in_french = True


# -----------------------------------------------------------------------------
# Greek
# -----------------------------------------------------------------------------

_EL_PRON_PATTERN = re.compile(r"ΔΦΑ.+\|([^}]+)")


def process_el(text: str) -> typing.Iterable[str]:
    """Process Greek pronunciations"""
    # Look for IPA pronunciations in -el- > προφορά (pronunciation) section.
    in_greek = False
    in_pron = False
    done_with_text = False

    for line in text.splitlines():
        if done_with_text:
            break

        line = line.strip()

        if in_greek and in_pron:
            if line.startswith("="):
                # New section
                done_with_text = True
                break

            for ipa_pron in _EL_PRON_PATTERN.findall(line):
                ipa_pron = ipa_pron.lower()
                ipa_pron = _refine_pron(ipa_pron)

                if ipa_pron:
                    yield ipa_pron
        elif in_greek and (line == "==={{προφορά}}==="):
            in_pron = True
        elif line == "=={{-el-}}==":
            in_greek = True


# -----------------------------------------------------------------------------

# Taken from https://github.com/Kyubyong/pron_dictionaries
def _refine_pron(pron):
    """Refines pronunciation (string)"""
    # remove punctuations
    pron = re.sub(r"[\u2000-\u206F.,·/#!$%\^&*;:{}=\-_`~()<>\[\]|]", "", pron)

    # unicode normalization
    pron = unicodedata.normalize("NFD", pron)

    # digraph normalization
    for k, v in _DIGRAPHS.items():
        pron = pron.replace(k, v)

    # split into single phonemes
    # stress symbols
    pron = re.sub("[ʼ']", "ˈ", pron)
    pron = re.sub("([ˈˌ])", r" \1", pron)

    # diacritics must combine with their preceding letters.
    pron = re.sub(r"([^\U00000300-\U0000036F\U000002B0-\U000002FF])", r" \1", pron)

    # remove spaces
    pron = re.sub("[ ]+", "", pron)

    return pron.strip()


# -----------------------------------------------------------------------------
