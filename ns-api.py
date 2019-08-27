# # NextPrime Python API demo
#
# Quick Jupyter lesson: It's like an interactive Python. Press `Shift Return` with the cursor in a cell; this sends the cell's code to the interpreter, prints its output and advances to the next cell.

import nprime_api
import uuid
# %load_ext autoreload
# %autoreload

# ## Configuration
#
# Your credentials go here.

username = "username"
apikey = "apikey"
venue = "venue"
npsf = nprime_api.Config(username, apikey)

# ## The Session object
#
# Sessions support connection reuse. 

s = npsf.new()

s.ping()

s.get_all_balances(currency_list=["jpy"])

s.close()

# You can use a `with` handler to ensure the connection is closed.

with npsf.new() as s:
    print (s.ping())
    print (s.get_all_balances(currency_list=["jpy"]), "\n")
    print (s.get_balance_for_user(username), "\n")
    print (s.get_balance_for_user(username, currency_list=["jpy"]))

# ## Trade data
#
# Please consult the API documentation for detailed semantics.

txid = str(uuid.uuid4())

trade_data = dict(
    trader=username,
    venue=venue,
    txid=txid,
    side="SELL",
    symbol="BTCUSD",
    price="17.47",
    size="100",
    tradetime="20190807-20:03:22.243",
    cost="1747.00",
    cost_ccy="USD",
    fees="0.01",
    fees_ccy="USD"
)

with npsf.new() as s:
    print (s.post_trade(trade_data, show_balances=True))
