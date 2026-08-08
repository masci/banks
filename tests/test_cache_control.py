from banks.filters.cache_control import cache_control


def test_cache_control(jinja_context, unwrap_content_block):
    res = cache_control(jinja_context, "foo", "ephemeral")
    res = unwrap_content_block(res)
    assert res == (
        '{"type":"text","cache_control":{"type":"ephemeral"},"text":"foo","image_url":null,"input_audio":null,'
        '"input_video":null,"input_document":null}'
    )
