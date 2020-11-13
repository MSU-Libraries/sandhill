import click
import sass
import os
from sandhill import app


@app.cli.command("compile-scss")
@click.option("--scss-dir", "-s", help="SCSS directory to compile")
@click.option("--css-dir","-c", help="CSS directory to save the output")
def compile_scss(scss_dir = None, css_dir = None):
    '''
    Given a provided scss directory, compile the discovered .scss files
    and save the results to the css directory.
    args:
        scc_dir (str) [Optional]: Path to search for scss files
            default: instance directory + static/scss
        css_dir (str) [Optional]: Path to output the compiled css
            default: instance directory + static/css
    returns:
        (int): exit code. 
            0 for success 
            1 for failure
    raises:
        click.ClickException: When the command is unsuccessful
    example:
        env/bin/flask compile-scss -s /scss -c /css
        env/bin/flask compile-scss
    '''
    errors = run_compile(scss_dir, css_dir)
    if errors:
        click.echo(click.style(errors, bold=True, fg='red'))
        raise click.ClickException("Command failed.")

    click.echo(click.style("Success!", bold=True))
    return 0

def run_compile(scss_dir = None, css_dir = None):
    '''
    Given a provided scss directory, compile the discovered .scss files
    and save the results to the css directory.
    args:
        scc_dir (str) [Optional]: Path to search for scss files
            default: instance directory + static/scss
        css_dir (str) [Optional]: Path to output the compiled css
            default: instance directory + static/css
    returns:
        (str): any error that occured
    '''
    # Set the default to the instance path location
    scss_dir = os.path.join(app.instance_path, 'static/scss') if not scss_dir else scss_dir
    css_dir = os.path.join(app.instance_path, 'static/css') if not css_dir else css_dir

    # Make sure the directories exist
    if not os.path.exists(scss_dir):
        return f"scss-dir path does not exist. {scss_dir}"
    if not os.path.exists(css_dir):
        return f"css-dir path does not exist. {scss_dir}"

    # Try to compile!
    try:
        sass.compile(dirname=(scss_dir, css_dir))
    except sass.CompileError as serr:
        return f"Unable to compile scss in dir {scss_dir}: {exc.code} {exc.name} {exc.description}"

    # Everything went fine
    return ""
