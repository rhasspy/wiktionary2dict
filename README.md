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

Using [gruut](https://github.com/rhasspy/gruut), you can phonemeize these pronunciations:

```sh
$ zcat en-us_lexicon.txt.gz | gruut en-us phonemize-lexicon | head -n 25
0 oʊ
101 w ʌ n oʊ w ʌ n
2.0 t uː p ɔɪ n t oʊ
6x6 s ɪ k s b ɑ ɪ s ɪ k s
747 s ɛ v ə n f oʊ ɹ t i s ɛ v ə n
aabomycin æ b oʊ m ɑ ɪ s ɪ n
aachen ɑ k ə n
aalborg ɔ l b ɔ ɹ
aam ɑ m
aandblom ɑ n t b l ɑ m
aardvark ɑ ɹ d v ɑ ɹ k
aasvoel ɑ s f oʊ ə l
ababda ə b æ b d ə
ababdeh ə b æ b d ɛ
abacisci æ b ə s ɪ s ɑ ɪ
abacost æ b ə k ɑ s t
abakan ɑ b ə k ɑ n
abarognosis æ b ə ɹ ə ɡ n oʊ s ɪ s
abarthroses æ b ɑ ɹ θ ɹ oʊ s i z
abatises æ b ə t ə s ə z
abatjour ɑ b ɑ ʒ ʊ ɝ
abat-voix ɑ b ɑ v w ɑ
abat-voix ɑ b ɑ v w ɑ z
abatvoix ɑ b ɑ v w ɑ
abbacy æ b ə s i
```
