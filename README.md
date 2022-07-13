# rustmaps.py

This package provides a Python interface for [rustmaps.com's HTTP REST API][1].

**NB:** This is my first API wrapper package so it may have some issues. If you
find any I would greatly appreciate it if you opened an issue or pull request!


## Roadmap to 1.0.0

The current features are not implemented:

- [ ] `maps/filter/{filterId}` endpoint (paginated map searching)
- [ ] v2Beta endpoints (`beta/outposts` and `beta/map/custom`)


## Contributing

This project uses flake8 with default settings. Please make sure your code
passes `poetry run flake8` and `poetry run pytest` before opening a pull
request.

This project is designed to work with Python 3.8.0+. Please do not open pull
requests with features that break this compatibility.


[1]: https://rustmaps.com/docs/index.html
