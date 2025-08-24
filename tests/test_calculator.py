from agent.tools.calculator import execute

def test_plain():
    assert execute("23*17+88") == "479"

def test_natural_language():
    assert execute("What is 23*17 + 88?") == "479"

def test_trigger():
    assert execute("[[calc: 23*17+88]]") == "479"

def test_dict_json():
    assert execute({"expression": "23*17+88"}) == "479"
    assert execute('{"tool":"calculator","args":{"expression":"23*17+88"}}') == "479"
