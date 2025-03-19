from banks.filters.cache_control import cache_control


def test_cache_control():
    res = cache_control("foo", "ephemeral")
    res = res.replace("<content_block>", "")
    res = res.replace("</content_block>", "")
    assert (
        res == '{"type":"text","cache_control":{"type":"ephemeral"},"text":"foo","image_url":null,"input_audio":null}'
    )
