"""Context related functionality"""
from datetime import datetime
from sandhill import app

def list_custom_context_processors():
    """
    Get a list of the current custom context processors
    returns:
        (list): A list of strings of the names
    """
    custom = []
    for entries in app.template_context_processors[None]:
        ctx_procs = entries()
        for key in ctx_procs:
            if key not in ['g', 'request', 'session']:
                custom.append(key)
    return custom

@app.context_processor
def context_processors():
    """
    Added context processor functions
    """
    def strftime(fmt: str = None, day: str = None) -> str:
        """
        Wrapper around datetime.strftime with default yyyy-mm-dd format
        args:
            fmt (str): The format for the date to return
            day (str): A date in yyyy-mm-dd format to format, or today if not passed
        returns:
            (str): The formatted date
        """
        fmt = "%Y-%m-%d" if not fmt else fmt
        day = datetime.now() if not day else datetime.strptime(day, "%Y-%m-%d")
        return day.strftime(fmt)

    def sandbug_context(value: str, comment: str = None):
        """
        Sandbug as a context processor, because we can.
        """
        sandbug(value, comment) # pylint: disable=undefined-variable

    return {
        'debug': app.debug,
        'strftime': strftime,
        'sandbug': sandbug_context
    }
