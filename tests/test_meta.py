from fastchecks import meta


def test_meta_basic_properties():
    assert meta.NAME is not None
    assert meta.VERSION is not None
    assert meta.DESCRIPTION is not None
    assert meta.WEBSITE is not None
