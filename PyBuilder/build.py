import os
from pybuilder.core import task, init, use_plugin, Author

use_plugin("python.core")
use_plugin("python.pycharm")
use_plugin("python.install_dependencies")

authors = [Author('Valentin Laquit', 'valentin.laquit@gmail.com')]

description = "This is the EASE MAPE System from Polytechnique Montreal"

name = "EASE_MAPE_System"

version = '0.2'

default_task = "install_dependencies"


@init
def set_properties(project):
    project.depends_on("docker")
    project.depends_on_requirements("requirements.txt")

