# nprime-api

Install [pipenv](https://docs.pipenv.org/en/latest/) through your choice of methods. It's available from Homebrew, for instance: `brew install pipenv`.

## Installing dependencies

```
pipenv sync --dev
```

## Opening the Jupyter notebook

You'll need to change the username, apikey, and venue.

```
pipenv run jupyter notebook ns-api.ipynb
```

## Running the bare sample

You'll need to edit `ns-api.py` to fix the username, apikey, and venue.

```
pipenv run python ns-api.py
```

##  Listening with the WS sample

```
pipenv run python wss_client.py --help
```

Note that this example's default endpoint is hardwired to the test environment; see `WSSClient.__init__`.
