
## ⏰ Automation (Daily Run) *optional and not tested

### Windows (Task Scheduler)

1. **Create a batch file** (e.g., `run_news.bat`) that activates your venv and runs the script:

   ```bat
   @echo off
   REM === adjust these paths ===
   set PROJECT_DIR=C:\Users\Steve\projects\fetch-news
   set VENV_DIR=%PROJECT_DIR%\.venv
   set PYTHON=%VENV_DIR%\Scripts\python.exe

   cd /d "%PROJECT_DIR%"
   "%PYTHON%" top_news_aggregator.py --include-world --include-us --include-ai --format html --output-file "%PROJECT_DIR%\top_news.html" --quiet
   ```

   > Tip: Test by double-clicking `run_news.bat` first.

2. **Schedule it**:
   - Open **Task Scheduler** → **Create Task…**
   - **General**: Name it *Top News Daily*, choose *Run whether user is logged on or not*.
   - **Triggers**: *New…* → Daily at **8:00 AM** (or your preferred time).
   - **Actions**: *New…* → **Start a program**  
     - *Program/script*: `C:\Windows\System32\cmd.exe`  
     - *Add arguments*: `/c "C:\Users\Steve\projects\fetch-news\run_news.bat >> C:\Users\Steve\projects\fetch-news\run.log 2>&1"`  
     - *Start in*: `C:\Users\Steve\projects\fetch-news`
   - **Conditions/Settings**: uncheck “Stop if running longer than…” if you prefer.

   The file will be written to `C:\Users\Steve\projects\fetch-news\top_news.html` each morning.

#### PowerShell alternative
Create `run_news.ps1`:
```powershell
$Project = "C:\Users\Steve\projects\fetch-news"
$VenvPy  = Join-Path $Project ".venv\Scripts\python.exe"
Set-Location $Project
& $VenvPy "top_news_aggregator.py" --include-world --include-us --include-ai --format html --output-file (Join-Path $Project "top_news.html") --quiet
```

Then schedule an **Action** with:
- *Program/script*: `powershell.exe`  
- *Add arguments*: `-ExecutionPolicy Bypass -File "C:\Users\Steve\projects\fetch-news\run_news.ps1"`

---

### Linux / macOS (cron)

1. Ensure the command works in your shell:
   ```bash
   cd /home/steve/projects/fetch-news
   . .venv/bin/activate
   python top_news_aggregator.py --include-world --include-us --include-ai --format html --output-file top_news.html --quiet
   ```

2. Add a crontab entry (runs daily at 08:00):
   ```bash
   crontab -e
   ```
   Add this line (adjust paths):
   ```cron
   0 8 * * * /usr/bin/env bash -lc 'cd /home/steve/projects/fetch-news && . .venv/bin/activate && python top_news_aggregator.py --include-world --include-us --include-ai --format html --output-file top_news.html --quiet >> /home/steve/projects/fetch-news/run.log 2>&1'
   ```

#### Optional: systemd user timer (Linux)
Create `~/.config/systemd/user/topnews.service`:
```ini
[Unit]
Description=Generate Top News HTML

[Service]
Type=oneshot
WorkingDirectory=%h/projects/fetch-news
ExecStart=%h/projects/fetch-news/.venv/bin/python %h/projects/fetch-news/top_news_aggregator.py --include-world --include-us --include-ai --format html --output-file %h/projects/fetch-news/top_news.html --quiet
```

Create `~/.config/systemd/user/topnews.timer`:
```ini
[Unit]
Description=Run Top News daily at 8 AM

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
systemctl --user daemon-reload
systemctl --user enable --now topnews.timer
```

---

### Viewing the HTML automatically
- **Windows**: add `start "" "C:\Users\Steve\projects\fetch-news\top_news.html"` as a second line in the batch file if you want it to open right after generation (omit when using Task Scheduler headless).  
- **macOS**: `open /Users/steve/projects/fetch-news/top_news.html`  
- **Linux**: `xdg-open /home/steve/projects/fetch-news/top_news.html`
