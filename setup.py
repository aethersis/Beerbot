from setuptools import setup

setup(
    name='Beerbot',
    description='An autonomous refridgerator robot that brings you beer when called',
    author='Maksym Walczak',
    author_email='maksym.walczak@gmail.com',
    url='https://github.com/aethersis/Beerbot',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: MIT License',
        'Operating System :: OS Independent (client), Raspbian (server)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Robotics',
    ],
    license='MIT',

    packages=['beerbot'],
    include_package_data=True,
    install_requires=[
        'pygame',
    ],
)
