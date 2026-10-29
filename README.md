# threads-cards

Image cards for the Threads account [@asan_busan_namja](https://www.threads.com/@asan_busan_namja).

- `make_card.py` renders a 1080x1350 PNG card from a small JSON file.
- `post.py` posts text or text + card to Threads from the cloud routine. It never handles the token; the cloud environment adds auth.
- `cards/` holds the cards attached to published posts. Threads fetches them from their raw GitHub URLs, so this repo is public.

```bash
pip install pillow
python make_card.py card.json out.png
```

Fonts in `fonts/` are NanumGothic by NAVER, licensed under the SIL Open Font License 1.1.
