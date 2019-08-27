#!/usr/bin/env python3
import sys
import argparse
import asyncio
import urllib
import urllib.parse
import json
from typing import Optional, List
import yaml
import websockets

# Sample WebSockets client for streaming balance updates from NextPrime.
# Requires:
# - python v3.7 or later
# - websockets module at: https://pypi.org/project/websockets/


class WSSClient(object):
    def __init__(self, actor: Optional[str], user: str, api_key: str,
            path: str = None, host: str = "test.npri.me"):
        """An base client class to observe NextPrime transactions.

        Override `consume`.

        :param actor: The account to observe; defaults to user
        :param user: The user to observe as
        :param api_key: The API key, used for authentication
        :param host: Hostname of service to connect to.
        :param file: Filepath to emit output or None for stdout
        """
        self.host: str = host
        self.actor: str
        self.fp: str

        if actor is None:
            self.actor = user
        else:
            self.actor = actor

        if path is None:
            self.fp = sys.stdout
        else:
            try:
                self.fp = open(path, 'w')
            except OSError:
                self.fp = sys.stdout

        self.user: str = user
        self.api_key: str = api_key
        self.ws: Optional[websockets.WebSocketClientProtocol] = None

    def _connect_string(self):
        path = f"/streams/{self.actor}/balances/{self.user}"
        # We have to be a little careful constructing this, due to
        # quoting issues in the username and api_key
        user = urllib.parse.quote(self.user)
        password = urllib.parse.quote(self.api_key)
        netloc = f"{user}:{password}@{self.host}"
        return urllib.parse.urlunsplit(('wss', netloc, path, None, None))

    async def run(self):
        async for message in self.ws:
            await self.consume(message)

    async def consume(self, message: str):
        """Process a trade report. This implementation prints it.

        :param message: The trade report, as a JSON string.
        """
        msg = json.loads(message)
        # Process the message how you'd like.
        # output to some file (usually stdout)
        s = yaml.safe_dump(msg, default_flow_style=False,
                           explicit_start=True, explicit_end=True)
        self.fp.write(s)

    async def subscribe(self):
        self.ws = await websockets.connect(self._connect_string())


parser = argparse.ArgumentParser(
    prog='wss-client',
    description='NextPrime example streaming client.'
)

parser.add_argument('-u', '--user', type=str, required=True,
                    metavar='USER', help='Username')
parser.add_argument('-p', '--api-key', type=str, required=True,
                    metavar='API_KEY', help='API key')
parser.add_argument('-a', '--actor', type=str, required=False,
                    metavar='ACTOR', help='Actor', default=None)


async def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)

    s = WSSClient(args.actor, args.user, args.api_key)

    try:
        await s.subscribe()
    except websockets.InvalidStatusCode as e:
        print(f"Invalid status code. Expected 100. Got {e.status_code}")
        return 1
    else:
        await s.run()
    return 0


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
