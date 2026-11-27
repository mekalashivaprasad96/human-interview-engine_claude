"""Module entrypoint allowing `python3 -m human_interview_engine`."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
