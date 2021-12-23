# FastAPI REST JSONAPI 🚀

# Setup

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Launch tests

### With coverage

```
pytest --cov=fastapi_rest_jsonapi --cov-report html tests/
```

### Without coverage

```
pytest
```

# Launch example app

```
uvicorn example.app:app --reload
```