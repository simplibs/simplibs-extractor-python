import pytest


@pytest.fixture(autouse=True)
def isolated_registries():
    """Give every test the registries of the extractor as they were at import, and put them back afterwards.

    `register_all` of an add-on writes into the registries of `simplibs-extractor`. Both are module-level
    dictionaries, so whatever one test registers would otherwise stay visible to every later test.
    """
    from simplibs.extractor.registry._helpers import PROFILE_REGISTRY, RENDERER_REGISTRY

    profiles = dict(PROFILE_REGISTRY)
    renderers = dict(RENDERER_REGISTRY)
    try:
        yield
    finally:
        PROFILE_REGISTRY.clear()
        PROFILE_REGISTRY.update(profiles)
        RENDERER_REGISTRY.clear()
        RENDERER_REGISTRY.update(renderers)
