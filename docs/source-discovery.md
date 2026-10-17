# Finding feeds for blogs without a known feed

Sources under `needs_research` in `axon-feed/config/sources.yaml` have no confirmed feed.
Never add a guessed URL. For each one:

1. **Look for an advertised feed.** Replace `PAGE` with the site's news/blog page:
   ```bash
   curl -sL -A "AxonFeedBot/0.1 (+https://github.com/gowthamsai09/Axon)" PAGE \
     | grep -iE '<link[^>]+rel="?alternate"?[^>]+(rss|atom)'
   ```
   Or in a browser: View Source and search for `application/rss+xml` / `application/atom+xml`.
2. **Check the sitemap.** Fetch `/robots.txt` (look for `Sitemap:`), then `/sitemap.xml`. A sitemap
   with dated URLs can be polled even without a feed.
3. **Check other first-party channels.** For open-model labs (Qwen, DeepSeek, Meta AI, Mistral),
   GitHub Releases / Atom feeds and Hugging Face org pages are often more reliable than a blog.
4. **Respect the rules.** Read `robots.txt` and the terms of service (spec Appendix B #11).
5. **Fall back** to the polite page scraper planned for Phase 1 (one plugin file plus a
   `sources.yaml` line) only when none of the above exists.
6. If you find a real feed URL, add it as a normal source with `verify: true`, run
   `python -m scripts.validate_sources --only <id>`, and remove the `needs_research` entry.
