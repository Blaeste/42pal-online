# Protocol of 42pal online

How the 42pal client talks to the 42pal server. The client is this repository; the server is private. This page covers the rules of every request, the login of a terminal, the ranked exam and its snapshots (plan: `docs/plans/42pal-online.md`).

## Every request

- **Server**: `https://<server>`, the address in `PAL42_SERVER` (`http://127.0.0.1:8000` until the domain is chosen). The API is under `/api/v1/`.
- **Body**: JSON in UTF-8, in both directions (`Content-Type: application/json`).
- **Version**: the client sends `X-42pal-Version: <its version>` (the one `./42pal --version` prints) with every API request. The server grades with the core of one version only: for any other version it answers `426` with the error `version`, and the client tells the student to update.
- **Errors**: any answer that is not `2xx` has the body `{"error": "<code>", "message": "<sentence>"}`. The code is for the program; the message, in English, is shown to the student as it is.
- **Login**: once a terminal is logged in, the client sends `Authorization: Bearer <token>`. A missing, unknown or revoked token gives `401` with the error `token`: the client says to log in again.

| Status | Error | When |
|---|---|---|
| 400 | `request` | the body is not the JSON expected |
| 401 | `token` | no token, or a token unknown or revoked |
| 403 | `refused` | the student refused the login, or the 42 account may not play ranked |
| 404 | `no_exam` | no ranked exam in progress (finished, or its time is up) |
| 404 | `unknown` | a grademe that is not the student's, or does not exist |
| 409 | `exam_running` | a ranked exam is already in progress: resume it first |
| 409 | `wait` | a grademe too early, before the wait after a failure is over |
| 409 | `grading` | the last grademe is still being graded |
| 409 | `variant` | a snapshot of another subject than the current one |
| 409 | `snapshot_chain` | a snapshot that does not follow the last one |
| 410 | `expired` | the pairing is too old, already used, or unknown |
| 426 | `version` | the client is not the version of the server |
| 429 | `busy` | too many requests; the message says when to try again |

## Logging in a terminal

`./42pal login` pairs the terminal with the student's 42 account. The secret of the 42 app never leaves the server: the browser does the 42 login with the server, and the terminal only waits for the result.

```mermaid
sequenceDiagram
    participant T as ./42pal login
    participant S as 42pal server
    participant B as Browser
    participant I as 42 intra
    T->>S: POST /api/v1/pairings
    S-->>T: device_code, user_code, login_url
    T->>B: opens login_url (/pair/USER-CODE)
    B->>S: GET /pair/USER-CODE
    S->>B: redirect to the 42 login
    B->>I: login, authorize the app
    I->>S: GET /auth/callback?code=...&state=...
    S->>I: POST /oauth/token, GET /v2/me
    S->>B: consent (first time), then "same code as your terminal?"
    B->>S: POST /pair/USER-CODE (confirm)
    loop every `interval` seconds
        T->>S: POST /api/v1/pairings/token
        S-->>T: 202 pending, then 200 with the token
    end
```

### `POST /api/v1/pairings`

Starts a pairing. Body: `{}`.

`201`:

```json
{
  "device_code": "a long random secret, known only by this terminal",
  "user_code": "BCDF-GHJK",
  "login_url": "https://<server>/pair/BCDF-GHJK",
  "interval": 2,
  "expires_in": 600
}
```

The client opens `login_url` in the browser and prints it with `user_code`: the page asks the student to check that the terminal shows the same code, so that a link sent by someone else cannot log in their terminal.

### `POST /api/v1/pairings/token`

Asks whether the student confirmed. Body: `{"device_code": "..."}`. The client asks every `interval` seconds, at most `expires_in` seconds.

- `202` `{"status": "pending"}`: not yet, ask again later.
- `200` `{"token": "...", "login": "jdoe", "campus": "Mulhouse"}`: logged in. The token is given once: the pairing is then used up.
- `403` `refused`: the student cancelled, or the account may not play ranked (the message says why).
- `410` `expired`: too late, or already used; run `./42pal login` again.

The client keeps the server, the token and the login in `~/.42pal/online.json`, readable by its owner only (mode 600). The server keeps only a hash of the token.

### `GET /api/v1/me`

Who the token belongs to. `200` `{"login": "jdoe", "campus": "Mulhouse", "kind": "student"}`; `kind` is `student` (the cursus), `pool` (a piscine in progress) or `alumni`; the server also keeps the promo (the year and month of the piscine) for the leaderboards. `./42pal ranked` offers the piscine exams to `pool`, those of the cursus to the others.

### `POST /api/v1/logout`

Revokes the token of the request. `204`, no body. `./42pal logout` then deletes `~/.42pal/online.json`; if the server cannot be reached, the file is deleted anyway and the client says the token is still valid on the server until the student deletes their account or logs out again.

### `DELETE /api/v1/account`

Withdraws the consent: the account and everything that is theirs go (exams, grademes, code, snapshots, the other terminals). `204`, no body. `./42pal delete-account` asks to type the login again first, then deletes `~/.42pal/online.json`; the site's account page does the same.

## The ranked exam

`./42pal ranked`. The server is the authority: it draws each subject from a secret seed, keeps the time (the real duration of the exam), the waits after a failure (the hard ones of the exam mode) and the levels, and grades the rendu again in a sandbox, with the tests of the variant plus those of a secret seed, new at each grademe. The client shows the subject from its own catalog (the same version as the server), grades the rendu itself first for the trace at once, then shows the server's verdict. One ranked exam at a time per student.

Every answer about an exam gives its state:

```json
{
  "exam": "rank02", "title": "Exam Rank 02",
  "level": 2, "variant": "char_position#3",
  "seconds": 1260, "seconds_left": 9540,
  "failures": 1, "wait_seconds": 24, "wait_if_ko": 150,
  "attempts": 3, "oks": 1, "passed_levels": [1], "grade": 25,
  "grading": null, "ended": false, "end": null
}
```

`variant` is the subject (`exo#seed`, as in the catalog). `wait_seconds` is the wait before the next grademe; `wait_if_ko` the one a failure would give. `grading` is the id of a grademe being graded, or `null`. When `ended` is true, `end` says how: `finish`, `time`, `passed` (100 points) or `no more levels`.

### `POST /api/v1/exams`

Body `{"exam": "rank02"}`, an exam of `exams/`. `201` with the state of the new exam; `409` `exam_running` if one is in progress.

### `GET /api/v1/exams/current`

`200` with the state of the exam in progress, to show it or resume it; `404` `no_exam` if there is none. An exam whose time is up ends here.

### `POST /api/v1/exams/current/grademe`

Body `{"files": {"<expected file>": "<content>"}, "local_passed": true}`: the files of the subject found in `rendu/<subject>/` (64 KiB each at most; no other name), and what the client's own grading said. `202` `{"grademe": 17}`; `409` `wait` or `grading`; `404` `no_exam`.

### `GET /api/v1/grademes/<id>`

`{"status": "queued"}` or `"running"` while it waits for a worker; the client asks again every second. Then `{"status": "done", "passed": false, "trace": "...", "tests_passed": 20, "tests_total": 25, "exam": {state}}`: the verdict, and the state it led to (the next level and subject, or the wait). `"status": "error"` means the server could not grade: no failure is counted, the student hands in again.

### `POST /api/v1/exams/current/finish`

Ends the exam now. `200` with its last state (`"ended": true`, the grade).

## Snapshots

While a ranked exam runs, the client sends a snapshot every 10 seconds, and a last one just before `finish`: the files of the subject changed since the last snapshot the server kept, or `{}` when nothing changed (a heartbeat). The server keeps each one with its own time; the anticheat reads them (what appears at once, the gaps).

### `POST /api/v1/exams/current/snapshots`

```json
{"seq": 12, "previous": "<hash of the last snapshot kept>", "variant": "char_position#3",
 "files": {"char_position.c": "..."}, "missed": 0}
```

`previous` is `""` for the first one. `missed` counts the sends that failed since the last one kept: that one carries every change since, so nothing is lost and the gap shows. `201` `{"seq": 12, "hash": "..."}`, the new link of the chain: the hash covers the one before and the content. `409` `snapshot_chain`: ask for the last link and send every file again; `409` `variant`: the subject just changed, the next snapshot will be of the new one; `429` `busy`: one every 3 seconds at most (256 KiB, 2400 per exam).

### `GET /api/v1/exams/current/snapshots/last`

`{"seq": 12, "hash": "..."}`, or `{"seq": 0, "hash": ""}` before the first: a terminal that resumes the exam follows the chain from there.

## Leaderboards

### `GET /api/v1/leaderboard?exam=rank02&promo=2024-07&campus=Mulhouse`

Every parameter is optional: without `exam`, the global score (the sum of each student's best grade per exam) of the cursus exams, or of the piscine exams with `audience=piscine`; without `promo`, the promo of the token's student (the year and month of their piscine), `all` for every promo; without `campus`, every campus. Validated exams only, all of them (no seasons). `200`:

```json
{"exam": "rank02", "audience": null, "promo": "2024-07", "campus": null,
 "rows": [{"rank": 1, "login": "jdoe", "campus": "Mulhouse", "grade": 75, "seconds": 6000}]}
```

Per exam, the best grade of each student, then the shortest time (`seconds`); students with the same grade and time share their rank. `seconds` is `null` in the global score; `promo` is `null` for every promo. `./42pal leaderboard [EXAM] [--promo P|all] [--campus C] [--piscine]` shows it; the site shows it too, to logged-in members only.

## Who may play ranked

The server reads `/v2/me` on the intra and lets in the active accounts of the 42 cursus (`student`), of a C piscine in progress (`pool`, the owner's choice) and the alumni; staff accounts and former students who are not alumni get `refused`. A cursus is in progress until its end date: 42 dropped the black hole, whose date can stay in the past on an active student. The offline modes stay open to everyone. The server keeps the 42 id, the login, the primary campus, the kind of account and the promo: nothing else from the intra (no email, no name, no picture).
