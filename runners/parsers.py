from runners.object_factory import object_factory


async def explain(href: str):
    return await object_factory(href=href).explain()


async def updates(href: str, **kwargs: dict):
    return await object_factory(href=href).run()
