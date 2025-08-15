# Familjens elpris – Root-only (utan mappar, utan Actions)

Det här paketet kan laddas upp direkt till repo-roten. Ingen mapp behöver skapas.
**Nackdel:** Ingen automatisk uppdatering via GitHub Actions (kräver mappar). Du uppdaterar genom att generera en ny `data.json` och ladda upp den.

## Snabbstart
1. Skapa ett **public** GitHub-repo.
2. Ladda upp filerna: `index.html`, `style.css`, `data.json` (kan saknas första gången), `fetch_nordpool.py`, `README-ROOT-NOACTIONS.txt`.
3. **Settings → Pages**: Branch `main`, Folder `/root` → Save.
4. Öppna Pages-URL:en (lägg som ikon i mobilen/iPad).

## Uppdatera priser (manuellt)
Varje gång du vill uppdatera sidan:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install nordpool pandas pytz
python fetch_nordpool.py
```
Det skapar/uppdaterar `data.json`. Gå till GitHub → **Add file → Upload files** → ladda upp **endast** `data.json` → Commit.

## Tips
- Vill du ha automatiska uppdateringar? Då **måste** GitHub Actions ligga i `.github/workflows/`.
  Det går att skapa *just den* mappen via “Create new file” med namn `.github/workflows/update.yml` och klistra in workflow-koden jag gav tidigare.
