import os
import pytest
from diceware.wordlist import (
    WORDLISTS_DIR, RE_WORDLIST_NAME, get_wordlist, get_wordlist_path,
    get_wordlist_names,
)


@pytest.fixture(scope="function")
def wordlists_dir(request, monkeypatch, tmpdir):
    """This fixture provides a temporary wordlist dir.
    """
    monkeypatch.setattr("diceware.wordlist.WORDLISTS_DIR", str(tmpdir))
    return tmpdir


class Test_GetWordList(object):

    def test_get_wordlist_en_8k(self):
        # we can get a list of words out of english 8k wordlist.
        en_src = os.path.join(WORDLISTS_DIR, 'wordlist_en_8k.txt')
        with open(en_src, 'r') as fd:
            en_result = get_wordlist(fd)
        assert en_result[0] == 'a'
        assert en_result[-1] == '@'
        assert len(en_result) == 8192

    def test_get_wordlist_simple(self, tmpdir):
        # simple wordlists can be created
        in_file = tmpdir.mkdir("work").join("mywordlist")
        in_file.write("a\nb\n")
        with open(in_file.strpath, 'r') as fd:
            result = get_wordlist(fd)
        assert ['a', 'b'] == result

    def test_get_wordlist_ignore_empty_lines(self, tmpdir):
        # we ignore empty lines in wordlists
        in_file = tmpdir.mkdir("work").join("mywordlist")
        in_file.write("\n\na\n\n")
        with open(in_file.strpath, 'r') as fd:
            result = get_wordlist(fd)
        assert ['a'] == result

    def test_get_wordlist_closes_fd(self, tmpdir):
        # we close passed-in file descriptors
        in_file = tmpdir.join("somewordlist")
        in_file.write("aaa\nbbb\n")
        with open(in_file.strpath, 'r') as fd:
            get_wordlist(fd)
            assert fd.closed is True


class TestWordlistModule(object):

    def test_re_wordlist_name(self):
        # RE_WORDLIST_NAME really works
        # valid stuff
        assert RE_WORDLIST_NAME.match('de') is not None
        assert RE_WORDLIST_NAME.match('DE') is not None
        assert RE_WORDLIST_NAME.match('vb') is not None
        assert RE_WORDLIST_NAME.match('8k') is not None
        assert RE_WORDLIST_NAME.match('original') is not None
        assert RE_WORDLIST_NAME.match('with_underscore') is not None
        assert RE_WORDLIST_NAME.match('u') is not None
        assert RE_WORDLIST_NAME.match('with-hyphen') is not None
        # invalid stuff
        assert RE_WORDLIST_NAME.match('with space') is None
        assert RE_WORDLIST_NAME.match('"with-quotation-marks"') is None
        assert RE_WORDLIST_NAME.match("'with-quotation-marks'") is None
        assert RE_WORDLIST_NAME.match('with.dot') is None
        assert RE_WORDLIST_NAME.match('with/slash') is None

    def test_get_wordlist_path(self):
        # we can get valid wordlist paths
        assert os.path.exists(get_wordlist_path('en_8k'))
        assert not os.path.exists(get_wordlist_path('zz'))

    def test_get_wordlist_path_requires_ascii(self):
        # non ASCII alphabet chars are not accepted in language specifier
        with pytest.raises(ValueError) as exc_info:
            get_wordlist_path('../../tmp')
        assert exc_info.value.args[0].startswith(
            'Not a valid wordlist name')

    def test_get_wordlist_names(self, wordlists_dir):
        # we can get wordlist names also if directory is empty.
        wlist_path = wordlists_dir.join('mywordlist_en_8k.txt')
        wlist_path.write("some\nirrelevant\nwords")
        assert get_wordlist_names() == ['en_8k']

    def test_get_wordlist_names_files_only(self, wordlists_dir):
        # non-files are ignored when looking for wordlist names
        sub_dir = wordlists_dir.mkdir('subdir')                # a subdir
        sub_dir.join("somfile_name.txt").write("Some\ntext")   # and a file in
        assert get_wordlist_names() == []

    def test_get_wordlist_names_requires_underscore(self, wordlists_dir):
        # we only recognize wordlist files with underscore in name
        wordlists_dir.join("file-without-underscore.txt").write("a\nb\n")
        assert get_wordlist_names() == []

    def test_get_wordlist_names_requires_dot(self, wordlists_dir):
        # we only recognize wordlist files with dot in name
        wordlists_dir.join("file_without_dot-in-name").write("a\nb\n")
        assert get_wordlist_names() == []
