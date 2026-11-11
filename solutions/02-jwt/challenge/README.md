# Challenge solution
Run from `../core`, with that directory on Python's import path:

```bash
python -m uvicorn extension:app --app-dir ../challenge --reload
```

Stop the core server first. This imports the core application and adds the optional extension. See the lab's challenge criteria for expected behaviour. No live credentials are supplied.
