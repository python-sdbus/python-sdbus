project('python-sdbus', 'c')

python_module = import('python')

python = python_module.find_installation('python3')

mypy = find_program(
    'mypy',
    required : false,
)
flake8 = find_program(
    'flake8',
    required : false,
)
linter_script = files('./tools/run_py_linters.py')

if mypy.found() and flake8.found()
    run_target(
        'lint-python',
        command : [python, linter_script, 'lint'],
    )
else
    warning('Mypy or Flake8 not found. Python linting disabled')
endif


autopep8 = find_program(
    'autopep8',
    required : false,
)
isort = find_program(
    'isort',
    required : false,
)

if autopep8.found() and isort.found()
    run_target(
        'format-python',
        command : [python, linter_script, 'format'],
    )
else
    warning('autopep8 or isort not found. Python formating disabled')
endif

subdir('src')
subdir('wheel-build')
