from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple

import requests
from requests import HTTPError


class NPSession(requests.Session):
    bare_prefix: str
    user: str
    prefix: str
    auth: Tuple[str, str]

    def __init__(self, bare_prefix: str, user: str, apikey: str, *args, **kwargs):
        """UNDOCUMENTED. Use nprime_api.Config.new() instead"""
        super(NPSession, self).__init__(*args, **kwargs)
        self.bare_prefix = bare_prefix
        self.user = user
        self.prefix = bare_prefix + "/" + user
        self.auth = (user, apikey)

    def ping(self) -> str:
        """Return the results of pinging the server"""
        r = self.get(self.bare_prefix + "/ping")
        r.raise_for_status()
        return r.text

    def get_all_balances(self, currency_list: Optional[List[str]] = None) -> Dict[str, dict]:
        """
        Return all accounts with balances associated with the account.

        Traders will see one element; exchanges will see themselves plus all customers.

        :param currency_list: An optional list of currency symbols; will limit responses to those currencies
        :type currency_list: Optional[List[str]]
        :return: A dictionary mapping accounts to balance/availability dicts
        :rtype: Dict[str, dict]
        """
        params = {}
        if currency_list is not None:
            params['ccy'] = currency_list
        r = self.get(self.prefix + "/balances", params=params)
        r.raise_for_status()
        return r.json()

    def get_balance_for_user(self, target_user: str, currency_list: Optional[List[str]] = None) -> dict:
        """
        Return the balance/available dict for a specific user.

        :param target_user: Either the current user, or if the current user is an exchange, a customer of the exchange
        :type target_user: str
        :param currency_list: An optional list of currency symbols; will limit responses to those currencies
        :type currency_list: currency_list: Optional[List[str]]
        :return: A balance/available dict
        :rtype: dict
        """
        params = {}
        if currency_list is not None:
            # raise NotImplementedError("Currently a server-side bug")
            params['ccy'] = currency_list
        r = self.get(self.prefix + "/balances/" + target_user, params=params)
        r.raise_for_status()
        return r.json()

    def get_my_balance(self, currency_list: Optional[List[str]] = None) -> dict:
        """
        Shortcut: using the get_balance_for_user mechanism, look up own balance
        :param currency_list: An optional list of currency symbols; will limit responses to those currencies
        :type currency_list: currency_list: Optional[List[str]]
        :return: A balance/available dict
        :rtype: dict
        """
        return self.get_balance_for_user(self.user, currency_list=currency_list)

    def post_trade(self, trade_dict: Dict[str, str], show_balances: bool=False) -> Optional[dict]:
        """
        Post a trade.
        :param trade_dict: A Python dict containing trade fields. See Swagger docs for model.
        :type trade_dict: Dict[str, str]
        :param show_balances: return balances as well
        :return: A JSON result
        :rtype: dict
        """
        endpoint = self.prefix + "/trades/new"
        if show_balances:
            endpoint += "?show_balances=yes"
        r = self.post(endpoint, json=trade_dict)
        r.raise_for_status()
        if not show_balances:
            return
        if r.status_code == 204:
            raise HTTPError("Empty message body when JSON expected", response=r)
        return r.json()


@dataclass
class Config(object):
    """
    A factory for NPSessions. NPSessions are the primary API.

    Sessions support support HTTP connection pooling.

    Typical use:

    cfg = nprime_api.Config("username", "apikey", "https://test.npri.me")
    with cfg.new() as s:
        print(s.ping())

    You don't have to use it as a connection handler:

    s = cfg.new()
    print(s.ping())
    s.close()
    """
    user: str
    apikey: str = field(repr=False)
    endpoint: str = "https://test.npri.me"

    def new(self) -> NPSession:
        """
        Build a new NPSession from current configuration.
        :return: The new NPSession
        :rtype: NPSession
        """
        bare_prefix = self.endpoint
        s = NPSession(bare_prefix, self.user, self.apikey)
        return s


SessionBuilder = Config
