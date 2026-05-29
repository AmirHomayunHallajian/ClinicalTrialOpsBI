from html.parser import HTMLParser
from pathlib import Path


class WebsiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.scripts = []
        self.stylesheets = []
        self.title_parts = []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attr_map = dict(attrs)
        if "id" in attr_map:
            self.ids.add(attr_map["id"])
        if tag == "a" and attr_map.get("href"):
            self.links.append(attr_map["href"])
        if tag == "script" and attr_map.get("src"):
            self.scripts.append(attr_map["src"])
        if tag == "link" and attr_map.get("rel") == "stylesheet":
            self.stylesheets.append(attr_map.get("href"))
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data.strip())


def parse_homepage():
    parser = WebsiteParser()
    parser.feed(Path("index.html").read_text(encoding="utf-8"))
    return parser


def test_homepage_assets_exist():
    parser = parse_homepage()
    for asset in [*parser.stylesheets, *parser.scripts]:
        assert Path(asset).exists(), f"Missing linked asset: {asset}"


def test_homepage_has_key_sections_and_title():
    parser = parse_homepage()
    assert "ClinicalTrialOpsBI" in " ".join(parser.title_parts)
    assert {"outcomes", "dashboard", "data-model", "workflow"}.issubset(parser.ids)


def test_navigation_targets_resolve():
    parser = parse_homepage()
    anchor_links = [link[1:] for link in parser.links if link.startswith("#") and len(link) > 1]
    assert anchor_links
    assert set(anchor_links).issubset(parser.ids)
