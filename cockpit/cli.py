import argparse
import json
import sys

from . import agents, ask as askmod, build, worry as worrymod


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cockpit", description="Veloxa CXO Cockpit. With no command it prints the top three things to worry about (CEO voice note T6a).")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("build", help="rebuild build/veloxa.db from data/raw")
    a = sub.add_parser("ask", help="ask one question")
    a.add_argument("question")
    a.add_argument("--as-of", help="YYYY-MM-DD (end of day IST) or ISO timestamp; default now")
    a.add_argument("--json", action="store_true")
    w = sub.add_parser("worry", help="full ranked list of what to worry about")
    w.add_argument("--as-of")
    t = sub.add_parser("top", help="top three things to worry about (default)")
    t.add_argument("--as-of")
    g = sub.add_parser("agent", help="show an agent card (name) or all")
    g.add_argument("who", nargs="?")
    s = sub.add_parser("serve", help="local web page: top three on open, ask box below")
    s.add_argument("--port", type=int, default=8000)
    s.add_argument("--as-of")
    sub.add_parser("test", help="run the automated question set")
    r = sub.add_parser("repl", help="interactive cockpit")
    r.add_argument("--as-of")
    args = ap.parse_args(argv)
    cmd = args.cmd or "top"
    as_of = getattr(args, "as_of", None)

    if cmd == "build":
        build.build()
        print("database built")
        return 0
    if cmd == "test":
        from tests.run_tests import run
        return run()
    if not build.DB.exists():
        build.build()
    if cmd == "ask":
        res = askmod.ask(args.question, as_of)
        print(json.dumps(res, indent=2) if args.json else askmod.format_result(res))
    elif cmd == "top":
        print("Top three things to worry about:\n")
        print(worrymod.format_worry(worrymod.worry(as_of), top=3))
    elif cmd == "worry":
        print(worrymod.format_worry(worrymod.worry(as_of)))
    elif cmd == "agent":
        print(agents.card(args.who) if args.who else agents.all_cards())
    elif cmd == "serve":
        from .serve import serve
        serve(args.port, as_of)
    elif cmd == "repl":
        print("Ask the cockpit (blank line to quit; 'worry' for the ranked list).")
        while True:
            try:
                q = input("> ").strip()
            except EOFError:
                break
            if not q:
                break
            print(worrymod.format_worry(worrymod.worry(as_of)) if q == "worry" else askmod.format_result(askmod.ask(q, as_of)))
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
