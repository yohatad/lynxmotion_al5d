from setuptools import setup
import os
from glob import glob

package_name = 'lynxmotion_al5d_description'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # Install launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),

        # Install URDF / xacro
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),

        # Install meshes
        (os.path.join('share', package_name, 'meshes/visual'), glob('meshes/visual/*')),
        (os.path.join('share', package_name, 'meshes/collision'), glob('meshes/collision/*')),

        # Install RViz configs
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*')),

        # Install config files
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),

        # Install models
        (os.path.join('share', package_name, 'models'), glob('models/*/*')),

        # Install worlds
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yoha',
    maintainer_email='yohatad000@gmail.com',
    description='Lynxmotion AL5D robot description with URDF/Xacro, Gazebo integration, and brick management services',
    license='BSD',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'brick_manager = lynxmotion_al5d_description.brick_manager:main',
        ],
    },
)