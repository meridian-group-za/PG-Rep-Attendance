# How to update the P&G Rep Attendance dashboard

Live site: https://meridian-group-za.github.io/PG-Rep-Attendance/

This folder is the master copy. Everything the dashboard needs lives here.

---

## Every day — nothing to do

August's numbers refresh automatically every day at **9:00am** on Carin's laptop
(a scheduled task called **"P&G Rep Attendance Daily Refresh"**). It reads the
latest `Rep Attendance Auto - August 2026.xlsx` and updates `attendance-data.js`
in this folder.

**This only works if Carin's laptop is on and signed in at 9am.** If it's off,
that day's refresh is skipped — it'll catch up the next time it's on at 9am.

**How to check it ran:** open `refresh_log.txt` in this folder. Every successful
run adds a line like:
```
2026-08-23 09:00:04 - OK
```
If you see `FAILED` instead, the workbook probably moved or was renamed — tell
whoever set this up (Carin / IT).

**The website itself does NOT update on its own** — the refresh only updates
the file on the laptop. See "Publishing changes" below to make the website
show the new data.

---

## When a new month starts (e.g. September)

1. **Get that month's Excel file.** It should be in:
   `Rep Attendance\Rep Attendance - <Month> 2026.xlsx`
   (one folder up from this one).

2. **Open a terminal in this folder** (right-click in the folder in File
   Explorer while holding Shift → "Open PowerShell window here", or use the
   address bar: type `powershell` and press Enter).

3. **Run this command**, replacing `<Month>` and `<CODE>` (a short 3-letter
   code, e.g. `SEP` for September, `OCT` for October):
   ```
   python extract_month.py "..\Rep Attendance - <Month> 2026.xlsx" <CODE> attendance-data-<code>.js ATTENDANCE_DATA_<CODE>
   ```
   Example for September:
   ```
   python extract_month.py "..\Rep Attendance - September 2026.xlsx" SEP attendance-data-sep.js ATTENDANCE_DATA_SEP
   ```
   It will print a summary like:
   ```
   wrote attendance-data-sep.js -> meta: {'totalTarget': ..., 'totalActual': ..., ...}
   ```
   If that number looks roughly sensible (matches what you'd expect for that
   month), it worked.

4. **This step needs a developer** (ask Claude / Carin to do it — it's a
   two-line edit): add the new month to the dashboard file
   (`P&G Rep Attendance Dashboard.dc.html`) so it shows up in the month
   dropdown. This is intentionally not something to hand-edit — a typo here
   breaks the whole dashboard.

5. **Publish the change** — see "Publishing changes" below.

---

## Publishing changes (making the website show your update)

The website (`https://meridian-group-za.github.io/PG-Rep-Attendance/`) only
updates when someone **pushes** the files from this folder to GitHub. This is
a deliberate manual step, not automatic — think of it like "save" on this
version, then "publish" as a separate button.

1. Open PowerShell in this folder (same as step 2 above).
2. Run these three commands, one at a time:
   ```
   git add .
   git commit -m "Update data"
   git push
   ```
3. Wait about a minute, then refresh the live site — your update will be there.

If `git push` gives an error you don't understand, stop and ask for help
rather than guessing — it usually means something needs to be fixed first,
not forced through.

---

## Quick reference

| Task | How often | Who | Automatic? |
|---|---|---|---|
| August data refresh | Daily | Nobody (scheduled task) | Yes, but laptop must be on at 9am |
| New month's data file | Monthly | Whoever gets the Excel | No — run `extract_month.py` |
| Add new month to dropdown | Monthly | Developer | No — needs a code edit |
| Push to make it live | After any change | Whoever made the change | No — `git push` |
