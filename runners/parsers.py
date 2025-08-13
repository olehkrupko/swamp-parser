import logging

from runners.object_factory import ObjectFactory


logger = logging.getLogger(__name__)


async def explain(href: str):
    return await ObjectFactory.create_object(href=href).explain()


async def updates(href: str, **kwargs: dict):
    return await ObjectFactory.create_object(href=href).run()
