import os

from pytest import fixture
from xprocess import ProcessStarter


@fixture
def chasm_server(xprocess, datadir):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    project_root = os.path.abspath(os.path.join(dir_path, '../../'))

    python_path = os.path.join(project_root, 'env/bin/python')
    chasm_server = os.path.join(project_root, 'chasmapp.py')
    config = os.path.join(project_root, 'config/dev.ini')

    class Starter(ProcessStarter):
        pattern = "Mined new block"

        args = ['python', chasm_server, '--config', config, '--dev']

    logfile = xprocess.ensure('Chasm Server', Starter, restart=True)
    yield logfile
    xprocess.getinfo('Chasm Server').terminate()
