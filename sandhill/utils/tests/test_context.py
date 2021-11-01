from sandhill.utils import context

def test_list_custom_context_processors():
    assert context.list_custom_context_processors() == [
        'debug',
        'strftime',
        'sandbug'
    ]

def test_context_processors():
    ctx = context.context_processors()

    assert isinstance(ctx['debug'], bool)
    assert ctx['strftime']('%Y-%m', '2021-08-31') == '2021-08'
    assert ctx['sandbug']('Test for sandbug context processor.') == None
