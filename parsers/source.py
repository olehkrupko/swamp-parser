import aiohttp


class Source:
    async def request(href, headers={}):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                href,
                headers=headers,
            ) as response:
                return await response.read()
