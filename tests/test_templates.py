'''
Tests the validate the Jinja2 syntax for all templates inside the /templates directory.
'''

import os
import pytest
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
from sandhill import app

def get_search_dirs():
    """
    Get the list of existing directories to search for templates
    """
    dirs = [os.path.join(app.root_path, "templates")]
    # Intentionally skip the test directory since that has invalid templates for testing purposes
    if "/tests/" not in app.instance_path:
        dirs.append(os.path.join(app.instance_path, "templates"))

    return [d for d in dirs if os.path.exists(d)]

def get_template_files():
    """
    Get a list of all template files from sandhill/templates and instance/templates
    """
    template_files = []

    for template_dir in get_search_dirs():
        for root, dirs, files in os.walk(template_dir):
            for f in files:
                if f.endswith(".j2") or f.endswith(".html"):
                    template_files.append((template_dir, os.path.join(root, f)))
    return template_files


def test_template_syntax():
    """
    Validate Jinja2 syntax for all templates in the app and instance directories
    """
    search_dirs = get_search_dirs()

    # Initialize a Jinja2 environment with the existing search paths
    env = Environment(loader=FileSystemLoader(search_dirs))

    # Register all custom filters, globals, and tests from the app
    env.filters.update(app.jinja_env.filters)
    env.globals.update(app.jinja_env.globals)
    env.tests.update(app.jinja_env.tests)

    template_entries = get_template_files()
    assert len(template_entries) > 0, "No templates found!"

    for base_dir, tpath in template_entries:
        # Get the path relative to its own base directory for the loader
        rel_path = os.path.relpath(tpath, base_dir)
        try:
            # Parse the file and raise TemplateSyntaxError if invalid
            env.get_template(rel_path)
        except TemplateSyntaxError as exc:
            pytest.fail(f"Jinja2 Syntax Error in {rel_path} (from {base_dir}) at line {exc.lineno}: {exc.message}")
        except Exception as exc:
            pytest.fail(f"Failed to load template {rel_path} (from {base_dir}): {exc}")
