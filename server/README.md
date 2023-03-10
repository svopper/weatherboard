# Weatherboard Server

## Setup

### Prepare

```bash
python -m venv --system-site-package venv
pip install requests pillow flask gunicorn pytz pycairo
cp fonts/* /usr/share/fonts/
fc-cache
```

### Run dev

```bash
FLASK_APP=server:app flask run --reload
```
