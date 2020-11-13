import click
import sass
import os
from sandhill import app


@app.cli.command("compile-scss")
@click.option("--scss-dir", "-s", help="SCSS directory to compile")
@click.option("--css-dir","-c", help="CSS directory to save the output")
def compile_scss(scss_dir, css_dir):
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
    # Set the default to the instance path location
    scss_dir = os.path.join(app.instance_path, 'static/scss') if not scss_dir else scss_dir
    css_dir = os.path.join(app.instance_path, 'static/css') if not css_dir else css_dir

    # Make sure the directories exist
    if not os.path.exists(scss_dir):
        click.echo(click.style(f"scss-dir path does not exist. {scss_dir}", bold=True, fg='red'))
        raise click.ClickException("Command failed.")
    if not os.path.exists(css_dir):
        click.echo(click.style(f"css-dir path does not exist. {scss_dir}", bold=True, fg='red'))
        raise click.ClickException("Command failed.")

    # Try to compile!
    try:
        sass.compile(dirname=(scss_dir, css_dir))
    except sass.CompileError as serr:
        click.echo(
            click.style(f"Unable to compile scss in dir {scss_dir}: ", bold=True, fg='red') + \
            f"{exc.code} {exc.name} {exc.description}"
        )
        raise click.ClickException("Command failed.")

    # Everything went fine
    click.echo(click.style("Compiled: ", bold=True) + click.style(css_dir, fg='green'))
    return 0
