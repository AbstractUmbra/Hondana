import asyncio

import hondana


# Here we can pass the `refresh_token` parameter.
# This is usually a large string (it is a json web token), so it may be wise to dynamically load and export this to a file for reading?
client = hondana.Client(refresh_token="...")


async def main():
    # We will attempt to log in. This will now skip the initial `/auth/login` endpoint and go straight to using your refresh token.
    await client.static_login()

    # For convenience, I have added the following:
    client.dump_refresh_token(file=True, path=".hondana_refresh", mode="w")
    # Which will dump your refresh token to a file

    await client.close()


asyncio.run(main())
