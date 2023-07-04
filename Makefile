update-tat:
	poetry run python lib/contabo_utils.py
	poetry run python lib/duckdb_utils.py

update-byob:
	cd services/byob_scraper && \
	poetry run python3.11 -m src.requests_entries && \
	poetry run python3.11 -m src.trades_spider

update-byob-trades:
	cd services/byob_scraper && \
	poetry run python3.11 -m src.trades_spider
