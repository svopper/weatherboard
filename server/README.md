# Weatherboard Server

## Setup

### Prepare

```bash
pip3 install requests pillow flask gunicorn pytz pycairo
cp fonts/* /usr/share/fonts/
fc-cache
```

### Run dev

```bash
FLASK_APP=server:app flask run --reload
```
