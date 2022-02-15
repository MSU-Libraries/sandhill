from sandhill import app

@app.template_filter()
def myfilter(value):
    return f"my{value}"
