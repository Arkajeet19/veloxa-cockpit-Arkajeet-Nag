"""Local page for the CEO: opens on the top three worries (T6a), with an ask box below.
Standard library only; binds to 127.0.0.1 so nothing is exposed on the network."""
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import ask as askmod, worry as worrymod

CSS = """body{font:16px/1.5 system-ui,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem;color:#1b1b1b;background:#fff}
@media(prefers-color-scheme:dark){body{background:#151515;color:#eee}.card{border-color:#444}.meta,.ev{color:#aaa}}
h1{font-size:1.4rem}.card{border:1px solid #ccc;border-radius:8px;padding:.8rem 1rem;margin:.8rem 0}
.meta,.ev{color:#555;font-size:.85rem}.tag{font-weight:600}input[type=text]{width:78%;padding:.5rem}button{padding:.5rem 1rem}
pre{white-space:pre-wrap;font:inherit}"""


def page(as_of, q=None):
    items = worrymod.worry(as_of)
    out = [f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Veloxa cockpit</title><style>{CSS}</style>",
           "<h1>What to worry about</h1><p class=meta>Top three, ranked by severity x confidence. Every item lists its evidence.</p>"]
    for n, i in enumerate(items[:3], 1):
        out.append(f"<div class=card><div><span class=tag>{n}. {html.escape(i['title'])}</span></div>"
                   f"<div class=meta>confidence {i['confidence']} | score {i['score']}</div>"
                   f"<p>{html.escape(i['why'])}</p><p><b>Do:</b> {html.escape(i['suggested_action'])}</p>"
                   f"<div class=ev>Evidence: {html.escape(', '.join(c['rec_id'] for c in i['citations'][:6]))}</div></div>")
    if len(items) > 3:
        out.append(f"<p class=meta>{len(items) - 3} more items are ranked below these: <a href='/all'>show all</a></p>")
    out.append("<h1>Ask a question</h1><form action=/ask><input type=text name=q placeholder='e.g. Is attrition high?' value='%s'> <button>Ask</button></form>" % html.escape(q or ""))
    if q:
        out.append("<div class=card><pre>%s</pre></div>" % html.escape(askmod.format_result(askmod.ask(q, as_of))))
    return "\n".join(out)


def all_page(as_of):
    return "<!doctype html><meta charset=utf-8><title>All risks</title><style>%s</style><h1>All ranked items</h1><div class=card><pre>%s</pre></div><a href=/>Back</a>" % (
        CSS, html.escape(worrymod.format_worry(worrymod.worry(as_of))))


def serve(port=8000, as_of=None):
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            u = urlparse(self.path)
            q = (parse_qs(u.query).get("q") or [None])[0]
            body = all_page(as_of) if u.path == "/all" else page(as_of, q) if u.path in ("/", "/ask") else None
            try:
                self.send_response(200 if body else 404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write((body or "not found").encode())
            except (ConnectionError, BrokenPipeError):
                pass  # the browser closed the connection (refresh, favicon, tab closed)

        def log_message(self, *a):
            pass
    print(f"Cockpit running at http://127.0.0.1:{port}  (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
