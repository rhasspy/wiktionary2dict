# Wiktionary2Dict

Command-line tool for extracting [International Phonetic Alphabet](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet) (IPA) word pronunciations from a [XML Wiktionary dump](http://ftp.acc.umu.se/mirror/wikimedia.org/dumps/) (`<LANG>wiktionary-<DATE>-pages-articles-multistream.xml.bz2`).

Inspired by https://github.com/Kyubyong/pron_dictionaries

See [gruut](https://github.com/rhasspy/gruut) for a pre-compiled set of lexicons.

## Dependencies

* Python 3.7 or higher
* lxml

## Supported Languages

Each language's wiktionary is slightly different, so custom processing functions are needed. The following languages have been tested:

* `de-de` (`dewiktionary`)
    * German
* `cs-cz` (`cswiktionary`)
    * Czech
* `en-us` (`enwiktionary`)
    * U.S. English
* `fr-fr` (`frwiktionary`)
    * French
* `it-it` (`itwiktionary`)
    * Italian
* `nl-nl` (`nlwiktionary`)
    * Dutch
    
## Installation

The use of a virtual environment is recommended for installation. The `create-venv.sh` script in the `scripts/` directory will handle most of the details for you:

```sh
$ git clone https://github.com/rhasspy/wiktionary2dict
$ cd wiktionary2dict
$ scripts/create-venv.sh
```

Once installation is completed, you should be able to run:

```sh
$ bin/wiktionary2dict --help
```

## Usage

First, download `<LANG>wiktionary/<LANG>wiktionary-<DATE>-pages-articles-multistream.xml.bz2` from [a mirror](http://ftp.acc.umu.se/mirror/wikimedia.org/dumps/) where `<LANG>` is the language and `<DATE>` is the date of the dump. For example:

```sh
$ wget enwiktionary-20200801-pages-articles-multistream.xml.bz2
```

Next, extract pronunciations and clean/sort/compress the resulting lexicon:

```sh
$ bzcat enwiktionary-20200801-pages-articles-multistream.xml.bz2 | \
    bin/wiktionary2dict en-us --casing lower | \
    sort | uniq | gzip -9 --to-stdout > en-us_lexicon.txt.gz
```

After it's finished, you can view a few entries with:

```sh
$ zcat en-us_lexicon.txt.gz | head -n 25
0 oʊ
101 ˈwʌnˌoʊ̯ˈwʌn
1080 tɛnˈʔeɪ̯ti
2.0 tupɔɪntoʊ
470 ˌfɔɹˈsɛvəɾ̃i
6x6 sɪksbaɪsɪks
747 ˌsɛvənfoɹtiˈsɛvən
aabomycin ˌæboʊˈmaɪsɪn
aachen ˈɑkən
aalborg ˈɔlbɔɹ
aam ɑm
aandblom ˈɑntblɑm
aardvark ˈɑɹdvɑɹk
aasvoel ˈɑsˌfoʊəl
ababda əˈbæbdə
ababdeh əˈbæbdɛ
abacisci ˌæbəˈsɪˌsaɪ
abacost ˈæbəkɑst
abakan ˌɑbəˈkɑn
abarognosis ˌæbəɹəɡˈnoʊsɪs
abarthroses ˌæˌbɑɹˈθɹoʊsiz
abatises ˈæbətəsəz
abatjour ˌɑˌbɑˈʒʊɚ
abatsons ˌɑˌbɑˈsɔ̃
abatsons ˌɑˌbɑˈsɔ̃z
```

## Adding a New Language

To add support for a new language, you must:

1. Create a `process_<LANG>` function in `__init__.py`
2. Add an entry to `__LANG_PROCESS` in `__main__.py`

Your `process_<LANG>` function should have the following form:

```python
def process_my_lang(text: str) -> typing.Iterable[str]:
    # Process content of <revision><text>...</text></revision>
    # yield IPA pronunciations
```

Because each language's Wiktionary is slightly different, you will need to inspect the XML yourself and determine the best way to extract pronunciations. Look at the existing `process_` functions for ideas of how to start.

Most of the `<text>` sections that you need to process contain MediaWiki markup. The desired IPA pronunciation is typically under a specific section/heading, and often begins with "IPA". Be careful to handle cases where multiple pronunciations from different regions (or even different languages) are all mixed together!
