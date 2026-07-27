from setuptools import find_packages, setup

package_name = "togo_status_handler"

# Installs this python package; takes the place of a CMakeLists for a purely Python package.
# The empty 'resource' file (also called a marker) helps ament know what packages are installed.
# See this discussion for more info:
#   https://robotics.stackexchange.com/questions/97794/ament-python-package-doesnt-explicitly-install-a-marker-in-the-package-index

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Emily Sheetz",
    maintainer_email="emily.j.sheetz@nasa.gov",
    description="Status handler for Togo, summarizing status information from Clearpath Husky A300 AMP.",
    license="TODO",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": ["togo_status_terminal = togo_status_handler.togo_status_terminal:main"],
    },
)
