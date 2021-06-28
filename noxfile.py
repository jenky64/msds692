import nox

nox.options.envdir = '/backup'

@nox.session(python=["3.7", "3.8"],venv_backend="conda")
def tests(session):
    session.conda_install('--channel=conda-forge', '--file', 'testing-modules-list.txt')
    session.conda_install('--channel=conda-forge', '--file', 'modules-list.txt')
    session.run('conda', 
            'develop', 
            '.',
            '--prefix', 
            session.virtualenv.location)

    session.run('pytest', '-vv', f'--html=test_results-{session.name}.html')

@nox.session(python=["3.8"],venv_backend="conda")
def lint(session):
    session.conda_install('flake8')
    session.run('flake8', 'anagram/')
