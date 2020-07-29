Hackernews fetcher
==================

As container
------------

```bash
docker build -t hackernews .
docker run --name hackernews_container -d -p8080:8080 hackernews
# visit http://localhost:8080
```

As python code
--------------

```bash
pipenv install -r requirements.txt
# Test
python -m pytest --verbose --exitfirst --capture=no --pythonwarnings ignore::DeprecationWarning
# Run
python main.py
# visit http://localhost:8080
```

Api
---

`/posts` - get posts in json  
`/posts?order=<col_name>[ desc|asc]` - sorting column with optional direction  
col_name can be: `id`, `title`, `url` or `created`  
`/posts?limit=<records_count>[&offset=<num>]` - limit number of shown records with optional offset
`/fetch_posts` - check for new hackerposts immediately 