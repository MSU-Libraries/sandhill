import os
import pytest
import shutil
from click.testing import CliRunner
from sandhill.commands import compile_scss
from sandhill import app

@pytest.fixture(scope='function')
def cleanup_compiled_css():
    shutil.rmtree(os.path.join(app.instance_path, 'static/css/compiled'))
    os.mkdir(os.path.join(app.instance_path, 'static/css/compiled'))

def test_compile_scss(cleanup_compiled_css):
    # Test calling through the click event with failure
    runner = CliRunner()
    result = runner.invoke(compile_scss.compile_scss, ['--scss-dir', '/dsffs', '--css-dir', 'ffs'])
    assert result.exit_code == 1
    assert 'does not exist' in result.output
    assert 'Command failed' in result.output

    # Test calling through the click event successfully
    runner = CliRunner()
    result = runner.invoke(compile_scss.compile_scss, [])
    assert result.exit_code == 0
    assert 'Success' in result.output

def test_run_compile_no_params(cleanup_compiled_css):
    # Test with defaults of instance directory
    errors = compile_scss.run_compile()
    assert not errors
    assert os.path.isfile(os.path.join(app.instance_path, 'static/css/compiled/test.css'))
    assert os.path.getsize(os.path.join(app.instance_path, 'static/css/compiled/test.css')) > 0

def test_run_compile_provide_dir(cleanup_compiled_css):
    # Test providing the directory
    errors = compile_scss.run_compile(
        os.path.join(app.instance_path, 'static/scss'),
        os.path.join(app.instance_path, 'static/css/compiled'))
    assert not errors
    assert os.path.isfile(os.path.join(app.instance_path, 'static/css/compiled/test.css'))
    assert os.path.getsize(os.path.join(app.instance_path, 'static/css/compiled/test.css')) > 0

def test_run_compile_invalid_path(cleanup_compiled_css):
    # Test providing invalid paths
    errors = compile_scss.run_compile("/sdfsdf","sdvv")
    assert errors
    assert "does not exist" in errors
    assert not os.path.isfile(os.path.join(app.instance_path, 'static/css/compiled/test.css'))
    errors = compile_scss.run_compile("/tmp","/sdvv")
    assert errors
    assert "does not exist" in errors
    assert not os.path.isfile(os.path.join(app.instance_path, 'static/css/compiled/test.css'))

def test_run_compile_invalid_path_type(cleanup_compiled_css):
    # Test providing invalid data types
    errors = compile_scss.run_compile(1, [True])
    assert errors
    assert "arguments were not string values" in errors
    assert not os.path.isfile(os.path.join(app.instance_path, 'static/css/compiled/test.css'))

def test_run_compile_invalid_scss(cleanup_compiled_css):
    # Test invalid scss file
    errors = compile_scss.run_compile(
        os.path.join(app.instance_path, 'static/scss_invalid'),
        os.path.join(app.instance_path, 'static/css/compiled_invalid'))
    assert errors
    assert "Unable to compile" in errors
    assert not os.path.isfile(os.path.join(app.instance_path, 'static/css/compiled_invalid/test.css'))
