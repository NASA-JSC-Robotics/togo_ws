from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'togo_apriltag'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ayammanu',
    maintainer_email='ananya.v.yammanuru@nasa.gov',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'apriltag_pos = togo_apriltag.apriltag_pos:main', 
            'rotate_only = togo_apriltag.rotate_only:main',
            'nav_to_apriltag = togo_apriltag.nav_to_apriltag:main'
            
            ],
    },
)
