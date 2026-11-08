# FastAPI Lab: Book Management API

Author: Arielle Whittle

This project manages books in memory through a FastAPI server and a Python command-line client. Book objects contain a nested author and a list of integer ratings. Requests and responses use JSON.

## Setup in VS Code (Mac or Codespaces)

1. Extract the downloaded ZIP. Open the extracted `fastapi_lab` folder in VS Code using File > Open Folder.
2. Select Terminal > New Terminal. Confirm this folder contains `requirements.txt`.
3. Run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python server/main.py
```

Leave this terminal running. The server starts at http://127.0.0.1:8000.
Open http://127.0.0.1:8000/docs for Swagger UI. In Codespaces, open port 8000 from the Ports tab and append `/docs` to the forwarded URL. Keep the forwarded port private.

4. In VS Code select Terminal > New Terminal again. Activate the same environment:

```bash
source .venv/bin/activate
```

Run every client command below from the project root. Do not close the server terminal.

## Demonstration commands

Run these in order after a fresh server start. New books initially receive ID 3.

```bash
python client/client.py list
python client/client.py get 1
python client/client.py create "Pride and Prejudice" "Jane Austen" "jane@example.com" 1813 "Romance" --ratings 4,5,3
python client/client.py get 3
python client/client.py update 3 "Pride and Prejudice" "Jane Austen" "jane@example.com" 1813 "Classic" --ratings 5,5
python client/client.py search-genre fiction
python client/client.py patch 3 --title "Pride and Prejudice (Updated)" --ratings 5,4,5
python client/client.py count
python client/client.py delete 3
python client/client.py count
python client/client.py get 999
python client/client.py --password wrong list
```

Expected results: list/get/update/search/patch/count/delete return 200, create returns 201, nonexistent ID returns 404, and incorrect credentials return 401. Count is 3 before deletion and 2 afterward.

Use `python client/client.py --help` for global options and `python client/client.py patch --help` for patch options. Global options go before the command. An empty author email string (`""`) represents no email. To clear ratings, use `--ratings ""`.

## All five exercises implemented

1. Genre search: GET `/books/genre/{genre}`; comparison is case-insensitive.
2. Ratings: `ratings` is a list of integers; create, update, and patch support `--ratings`.
3. PATCH: `/books/{book_id}` changes provided non-null fields; omitted fields remain unchanged. The client preserves existing nested author fields when changing only the author name or email.
4. HTTP Basic authentication: every book endpoint requires the lab credentials `admin` / `secret`. The client includes them on every request. Swagger UI's Authorize button accepts these credentials.
5. Count: GET `/books/count` returns `{"count": number}`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | /books | List all books |
| GET | /books/count | Count books |
| GET | /books/genre/{genre} | Search by genre |
| GET | /books/{book_id} | Retrieve a book |
| POST | /books | Create a book |
| PUT | /books/{book_id} | Replace a book |
| PATCH | /books/{book_id} | Partially update a book |
| DELETE | /books/{book_id} | Delete a book |

Duplicate IDs and mismatched PUT IDs return 400. Invalid request data returns 422. The client displays response status and JSON, handles non-JSON responses, and reports connection errors.

## Swagger testing

Open `/docs`, click Authorize, enter `admin` and `secret`, and close the dialog. Expand an endpoint, select Try it out, enter the parameters or JSON body, and click Execute.

Example POST body:

```json
{
  "id": 3,
  "title": "Pride and Prejudice",
  "author": {"name": "Jane Austen", "email": "jane@example.com"},
  "year": 1813,
  "genre": "Romance",
  "ratings": [4, 5, 3]
}
```

Do not create ID 3 in Swagger and then expect the client demonstration to create ID 3 again. Restart the server to reset the dataset before following the demonstration sequence.

## Screenshot checklist for the Word report

Take your own screenshots after running the project. Include readable commands and outputs.

1. Project files and successful server startup.
2. Swagger UI with the endpoints visible.
3. Client list/get showing nested author JSON.
4. Create with ratings (201) and full update (200).
5. Case-insensitive genre search.
6. PATCH response showing the title changed and other fields preserved.
7. Count before deletion, successful deletion, and count afterward.
8. A 404 missing-book response and a 401 authentication response.
9. Swagger execution showing a successful response and JSON data.

For each screenshot, write one or two sentences explaining the command, expected result, and observed result. Include your name, project purpose, setup process, all five exercises, JSON serialization explanation, and conclusion. The supplied assignment screenshots are instructions, not evidence of running the application.

## Design notes

Pydantic validates incoming JSON and serializes Book and Author models in responses. The requests client serializes Python dictionaries with its `json=` argument and deserializes responses with `.json()`. The server stores data only in a Python list: restarting resets all changes. Run one server process for this lab. The hardcoded credentials are demonstration credentials for this assignment. IDs are chosen as max current ID + 1 in the client, appropriate for this single-user demonstration.

## Submit to the assignment repository

Accept the professor's GitHub Classroom invitation and use the resulting assignment repository. Copy `server`, `client`, `requirements.txt`, `README.md`, `.gitignore`, and your completed Word report into that repository. Do not upload `.venv`.

In VS Code, open the assignment repository, select Source Control, review the changed files, stage them with +, enter a commit message such as `Complete FastAPI book lab`, select Commit, then Sync Changes or Push. Confirm the files appear on GitHub and submit the required repository link in Canvas.
