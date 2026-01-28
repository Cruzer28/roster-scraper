# Installation Troubleshooting Guide

## "command not found: pip" Error

This usually means pip isn't in your PATH or is named differently. Try these solutions:

### Solution 1: Use python -m pip (RECOMMENDED)
This always works because it uses Python's built-in module system:

```bash
cd roster_scraper
python3 -m pip install -r requirements.txt
python3 app.py
```

### Solution 2: Try pip3
On many systems, especially Mac/Linux, pip is called pip3:

```bash
pip3 install -r requirements.txt
python3 app.py
```

### Solution 3: Install with --user flag
If you get permissions errors:

```bash
python3 -m pip install -r requirements.txt --user
python3 app.py
```

### Solution 4: Check Your Setup
Run these to diagnose:

```bash
which python
which python3
which pip
which pip3
python3 --version
```

You need Python 3.7 or higher. If you see Python 2.x, use `python3` instead of `python`.

---

## Manual Installation (Step-by-Step)

If the run script doesn't work, do it manually:

### 1. Check Python Version
```bash
python3 --version
```
Should show 3.7 or higher.

### 2. Install Flask
```bash
python3 -m pip install flask --user
```

### 3. Install BeautifulSoup
```bash
python3 -m pip install beautifulsoup4 --user
```

### 4. Install Requests
```bash
python3 -m pip install requests --user
```

### 5. Run the App
```bash
python3 app.py
```

### 6. Open Browser
Go to: http://localhost:5000

---

## Common Errors & Fixes

### "No module named 'flask'"
**Fix:** Install with `python3 -m pip install flask --user`

### "Permission denied"
**Fix:** Add `--user` flag to install in your home directory
```bash
python3 -m pip install -r requirements.txt --user
```

### "Address already in use"
**Fix:** Port 5000 is taken. Either:
- Kill the other process: `lsof -ti:5000 | xargs kill`
- Or change the port in app.py (last line, change 5000 to 5001)

### Can't access http://localhost:5000
**Fix:** Try these URLs instead:
- http://127.0.0.1:5000
- http://0.0.0.0:5000

---

## Windows-Specific Issues

### If you're on Windows:

**Use Command Prompt or PowerShell, NOT Git Bash for pip**

```cmd
cd roster_scraper
python -m pip install -r requirements.txt
python app.py
```

### If python command doesn't work:
```cmd
py -3 -m pip install -r requirements.txt
py -3 app.py
```

---

## Mac-Specific Issues

### If you're on Mac with Apple Silicon (M1/M2/M3):

Make sure you're using the right Python:
```bash
which python3
/usr/bin/python3  # ✅ Good - system Python
/opt/homebrew/bin/python3  # ✅ Good - Homebrew Python
```

### If pip still doesn't work:
Install via Homebrew:
```bash
brew install python3
python3 -m pip install -r requirements.txt
```

---

## Nuclear Option: Virtual Environment

If nothing else works, use a virtual environment:

```bash
cd roster_scraper

# Create virtual environment
python3 -m venv venv

# Activate it (Mac/Linux)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate

# Now install
pip install -r requirements.txt

# Run app
python app.py
```

Now pip should definitely work because it's isolated.

---

## Still Not Working?

Send me:
1. Your operating system (Windows/Mac/Linux)
2. Output of: `python3 --version`
3. Output of: `python3 -m pip --version`
4. The exact error message you're seeing

I'll help you figure it out.
