# Nepal Live Weather Inference

Project 3 applies the global Project 1 data-agent package with the Nepal-specific Project 2 model package to identify weather shifts in Nepal.

## Local development setup

Install the two local dependencies first, then this project:

```powershell
pip install -e ..\global-weather-data-agent
pip install -e ..\nepal-timesfm-model
pip install -e .
nepal-live-inference "Namche Bazaar" --database ..\global-weather-data-agent\data\weather.sqlite3
```

For GitHub use, replace the two local installs with tagged package releases from Projects 1 and 2. The database is runtime state and must never be committed.

## License

MIT. See [LICENSE](LICENSE).

