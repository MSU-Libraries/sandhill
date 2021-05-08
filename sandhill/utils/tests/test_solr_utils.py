from sandhill.utils import solr

def test_Solr_encode_value():
    assert solr.Solr().encode_value("a value wild-card*") == "a\\ value\\ wild\\-card*"
    assert solr.Solr().encode_value("a value wild-card*", escape_wildcards=True) == "a\\ value\\ wild\\-card\\*"
    assert solr.Solr().encode_value("AIDS (Disease)--Prevention") == "AIDS\\ \\(Disease\\)\\-\\-Prevention"

def test_Solr_encode_query():
    assert solr.Solr().encode_query("a value wild-card*") == "a value wild\\-card*"
    assert solr.Solr().encode_query("a value wild-card*", escape_wildcards=True) == "a value wild\\-card\\*"
    assert solr.Solr().encode_query("test query OR (\"sub term\" AND other term)", escape_wildcards=True) == "test query OR (\"sub term\" AND other term)"
