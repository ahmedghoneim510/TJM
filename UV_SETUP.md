# UV Setup & Installation Guide

## 🚀 Install UV (if not already installed)

### Windows (PowerShell)

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or with pip:

```bash
pip install uv
```

---

## 📦 Project Setup with UV

### 1. Create and activate virtual environment

```bash
# Create virtual environment
uv venv

# Activate (PowerShell)
.venv\Scripts\Activate.ps1

# Or activate (CMD)
.venv\Scripts\activate.bat
```

### 2. Install all dependencies

```bash
# Install from pyproject.toml
uv pip install -e .

# Or sync with uv.lock
uv sync
```

### 3. Verify installation

```bash
# Check Python version
python --version  # Should be 3.11.x

# Check installed packages
uv pip list
```

---

## 🎯 Run the Project

### Test the grounding system

```bash
uv run python test_grounding.py
```

### Run the automation

```bash
uv run python main.py
```

Or after activating the virtual environment:

```bash
python test_grounding.py
python main.py
```

---

## 🔧 UV Commands Reference

```bash
# Install specific package
uv pip install package-name

# Add new dependency to project
uv add package-name

# Remove dependency
uv remove package-name

# Update all packages
uv sync --upgrade

# Show dependency tree
uv pip tree

# Export requirements.txt (if needed)
uv pip freeze > requirements.txt
```

---

## ⚙️ Alternative: Traditional pip (if UV not available)

```bash
# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\Activate.ps1  # PowerShell
# or
.venv\Scripts\activate.bat   # CMD

# Install dependencies
pip install -r requirements.txt
```

---

## 🎯 Prerequisites Checklist

- [x] Python 3.10+ installed
- [x] UV installed (or pip as fallback)
- [x] Virtual environment created
- [x] Dependencies installed
- [ ] **Notepad shortcut on desktop** (CRITICAL!)
- [x] Google API key configured (already in code)
- [ ] Internet connection active

---

## 🐛 Troubleshooting

### Issue: UV command not found

**Solution:** Restart your terminal after installing UV, or add `%USERPROFILE%\.cargo\bin` to PATH

### Issue: Python version mismatch

**Solution:**

```bash
uv python install 3.11
uv venv --python 3.11
```

### Issue: Package installation fails

**Solution:** Try pip fallback:

```bash
pip install -r requirements.txt
```

---

## 📚 Next Steps

After setup, see [QUICK_START.md](QUICK_START.md) for testing and running the automation.
