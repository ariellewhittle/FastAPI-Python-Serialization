"""Command-line client for the book API."""
import argparse
import json
import sys
from urllib.parse import quote

import requests


def ratings_list(value):
    try:
        return [int(item.strip()) for item in value.split(",")] if value else []
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use comma-separated integers, such as 4,5,3") from exc


def build_parser():
    parser = argparse.ArgumentParser(description="Book API client")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="secret")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    commands.add_parser("count")
    for command in ("get", "delete"):
        commands.add_parser(command).add_argument("id", type=int)
    commands.add_parser("search-genre").add_argument("genre")
    for command in ("create", "update"):
        sub = commands.add_parser(command)
        if command == "update":
            sub.add_argument("id", type=int)
        sub.add_argument("title")
        sub.add_argument("author_name")
        sub.add_argument("author_email", help="Use an empty string for no email")
        sub.add_argument("year", type=int)
        sub.add_argument("genre")
        sub.add_argument("--ratings", type=ratings_list, default=[])
    sub = commands.add_parser("patch")
    sub.add_argument("id", type=int)
    for field in ("title", "genre", "author-name", "author-email"):
        sub.add_argument("--" + field)
    sub.add_argument("--year", type=int)
    sub.add_argument("--ratings", type=ratings_list)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    session = requests.Session()
    session.auth = (args.username, args.password)
    base = args.url.rstrip("/")

    def request(method, path, **kwargs):
        return session.request(method, base + path, timeout=10, **kwargs)

    try:
        command = args.command
        if command in ("list", "count", "search-genre"):
            path = {"list": "/books", "count": "/books/count"}.get(command)
            if command == "search-genre":
                path = "/books/genre/" + quote(args.genre, safe="")
            response = request("GET", path)
        elif command in ("get", "delete"):
            response = request("GET" if command == "get" else "DELETE", f"/books/{args.id}")
        elif command in ("create", "update"):
            if command == "create":
                existing = request("GET", "/books")
                existing.raise_for_status()
                # max + 1 avoids collisions after deleting a book.
                book_id = max((book["id"] for book in existing.json()), default=0) + 1
            else:
                book_id = args.id
            payload = {
                "id": book_id, "title": args.title,
                "author": {"name": args.author_name, "email": args.author_email or None},
                "year": args.year, "genre": args.genre, "ratings": args.ratings,
            }
            response = request("POST" if command == "create" else "PUT",
                               "/books" if command == "create" else f"/books/{book_id}",
                               json=payload)
        else:
            payload = {key: getattr(args, key) for key in ("title", "year", "genre", "ratings")
                       if getattr(args, key) is not None}
            if args.author_name is not None or args.author_email is not None:
                existing = request("GET", f"/books/{args.id}")
                existing.raise_for_status()
                author = existing.json()["author"]
                if args.author_name is not None:
                    author["name"] = args.author_name
                if args.author_email is not None:
                    author["email"] = args.author_email or None
                payload["author"] = author
            if not payload:
                parser.error("patch requires at least one field, such as --title")
            response = request("PATCH", f"/books/{args.id}", json=payload)
        print(f"Status Code: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2))
        except ValueError:
            print(response.text)
        return 0 if response.ok else 1
    except requests.RequestException as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
