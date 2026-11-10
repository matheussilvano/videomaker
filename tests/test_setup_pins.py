import re

from videomaker.install import UPSTREAM
from videomaker.tts import MODEL_FILES, language_defaults


def test_upstream_skills_are_pinned_to_full_commits():
    for up in UPSTREAM:
        assert re.fullmatch(r"[0-9a-f]{40}", up.commit), up.link_name
        assert up.repo.startswith("https://github.com/")


def test_model_downloads_are_checksummed():
    for url, sha in MODEL_FILES.values():
        assert url.startswith("https://")
        assert re.fullmatch(r"[0-9a-f]{64}", sha)


def test_language_defaults_accept_region_codes():
    assert language_defaults("pt-BR") == ("pt-br", "pf_dora")
    assert language_defaults("en")[0] == "en-us"
