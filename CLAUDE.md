# Values 2060 survey - setup brief for Claude Code

## What this project is
UCD MIS20070 group project, Section 2. A mobile survey where respondents place one dot on a
ternary plot (Equality / Belonging / Purpose) for TODAY and one for 2060. Responses go to a
Google Sheet. We need 50+ responses, an Excel export, and an aggregated ternary plot in Python.

- `docs/index.html` - the finished survey (single file). GitHub Pages serves this folder.
- `backend/Code.gs` + `backend/appsscript.json` - Google Apps Script backend, bound to the Sheet.
- `analysis/plot_ternary.py` - turns the Excel export into the report chart + summary.csv.

## Rules
- Do NOT change the survey's design, copy, values or flow unless the user asks. The only edit
  needed in `docs/index.html` is the `ENDPOINT` line.
- Never ask for, type or store the user's passwords. Logins happen in the user's browser.
- At every CHECKPOINT, stop, tell the user in plain English exactly what to click, and wait
  for them to say done. The user is a business student, not a developer - be concrete and brief.
- Check `clasp --help` before using clasp commands; command names differ between versions
  (e.g. v3 uses `create-script` / `create-deployment` where v2 uses `create` / `deploy`).
- Use the user's OS conventions (macOS vs Windows) for any install commands.

## The flow

### 0. Prerequisites
Check for `node`, `npm`, `git`, `python3`, `gh`. Install what's missing (ask before installing
anything system-wide). Then `npm install -g @google/clasp`.
Python deps: `pip install pandas openpyxl matplotlib`.

### 1. Google access - CHECKPOINTS
a) CHECKPOINT: user opens https://script.google.com/home/usersettings and turns ON
   "Google Apps Script API".
b) Run `clasp login`. CHECKPOINT: user approves in the browser that opens.

### 2. Create the Sheet + backend
From `backend/`:
- Back up `Code.gs` and `appsscript.json` first (clasp may overwrite the manifest).
- Create a new Google Sheet with a bound script titled "Values 2060 responses"
  (`clasp create --type sheets --title "Values 2060 responses"` or the v3 equivalent).
- Restore our `Code.gs` and `appsscript.json` if they were overwritten, delete any stray
  default `Code.js`, then push with force.
- Note the Sheet URL that clasp prints - the user needs it.

### 3. Authorise the backend - CHECKPOINT
Open the script editor (`clasp open` / `clasp open-script`). CHECKPOINT: tell the user to pick
`setup` in the function dropdown, press Run, and approve permissions. Google will say
"Google hasn't verified this app": that is normal for your own script - click Advanced,
then "Go to (project)", then Allow. `setup()` creates the `responses` tab and headers.

### 4. Deploy the web app
Create a deployment (description "v1"). The manifest already sets execute-as-me and
access-anyone. Build the URL: `https://script.google.com/macros/s/<DEPLOYMENT_ID>/exec`.
Write the Sheet URL, script ID and deployment ID into `DEPLOYMENT.md`.
Test it:
- `curl -sL "<URL>"` should return `{"n":0,"points":[]}`.
- `curl -sL -H "Content-Type: text/plain" -d '{"respondent_id":"test-1","t":{"e":40,"b":30,"p":30},"f":{"e":20,"b":50,"p":30},"ua":"curl"}' "<URL>"`
  should return `{"ok":true,"n":1}`.
- Run the same POST again - should return `{"ok":false,"reason":"duplicate"}`.
If GET returns an HTML login page, access is not "Anyone" - check the deployment settings first.
ACCOUNT NOTE: the user is using their UCD Connect (university-managed Google Workspace) account.
University admins sometimes block anonymous web-app access or the Apps Script API. If anonymous
access is blocked by the domain (login page persists with correct settings, or "Anyone" is not
offered), STOP and tell the user plainly: the university account restricts it, and the fix is to
redo steps 1-4 with a personal Gmail account. Do not try to work around the restriction.

### 5. Connect the site
Copy `docs/index.html` to `/tmp/index.original.html` first. Then in `docs/index.html` set
`const ENDPOINT = '<URL>';` - change nothing else. Run a diff against the backup and confirm the
ONLY changed line is the ENDPOINT line. The user wants the live site to look exactly like the
approved mock-up, so no reformatting, no "improvements", no other edits.

### 6. Publish on GitHub Pages - CHECKPOINT
a) Run `gh auth login` if not logged in. CHECKPOINT: user completes it in the browser.
b) Add a `.gitignore` containing `.clasp.json`, `.clasprc.json`, `analysis/*.xlsx`, `__pycache__/`.
c) `git init`, commit everything, then `gh repo create values-2060 --public --source . --push`.
d) Enable Pages from `main` branch, `/docs` folder:
   `gh api -X POST repos/<owner>/values-2060/pages -f "source[branch]=main" -f "source[path]=/docs"`
e) Wait, then confirm `https://<owner>.github.io/values-2060/` returns 200.
Fallback if Pages fails: `npx netlify-cli deploy --prod --dir docs` (user logs in via browser).

### 7. Hand-off
Tell the user, in one short message:
- the live survey link, the Google Sheet link, the GitHub repo link
- to delete the "test-1" row from the Sheet (keep row 1 headers)
- to test on their own phone, then use a private tab to test once more, delete those rows,
  and only then share the link widely
- that after any backend edit you must redeploy to the SAME deployment ID, never a new one

## Later: the report chart (once 50+ responses are in)
User downloads the Sheet as Excel (File > Download > .xlsx) into `analysis/responses.xlsx`.
Run `python analysis/plot_ternary.py analysis/responses.xlsx`. Show the user
`analysis/ternary_aggregated.png` and the `summary.csv` numbers, and help them interpret the
shifts for the 250-350 word analysis. Commit the script and the chart (not the xlsx).
