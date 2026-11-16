import argparse
import json
import sys

from . import agents, ask as askmod, build, worry as worrymod


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cockpit", description="Veloxa CXO Cockpit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="rebuild build/veloxa.db from data/raw")
    a = sub.add_parser("ask", help="ask one question")
    a.add_argument("question")
    a.add_argument("--as-of", help="YYYY-MM-DD (end of day IST) or ISO timestamp; default now")
    a.add_argument("--json", action="store_true")
    w = sub.add_parser("worry", help="ranked list of what to worry about")
    w.add_argument("--as-of")
    g = sub.add_parser("agent", help="show an agent card (name) or all")
    g.add_argument("who", nargs="?")
    sub.add_parser("test", help="run the automated question set")
    r = sub.add_parser("repl", help="interactive cockpit")
    r.add_argument("--as-of")
    args = ap.parse_args(argv)

    if args.cmd == "build":
        build.build()
        print("database built")
        return 0
    if args.cmd == "test":
        from tests.run_tests import run
        return run()
    if not build.DB.exists():
        build.build()
    if args.cmd == "ask":
        res = askmod.ask(args.question, args.as_of)
        print(json.dumps(res, indent=2) if args.json else askmod.format_result(res))
    elif args.cmd == "worry":
        print(worrymod.format_worry(worrymod.worry(args.as_of)))
    elif args.cmd == "agent":
        print(agents.card(args.who) if args.who else agents.all_cards())
    elif args.cmd == "repl":
        print("Ask the cockpit (blank line to quit; 'worry' for the ranked list).")
        while True:
            try:
                q = input("> ").strip()
            except EOFError:
                break
            if not q:
                break
            print(worrymod.format_worry(worrymod.worry(args.as_of)) if q == "worry" else askmod.format_result(askmod.ask(q, args.as_of)))
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
