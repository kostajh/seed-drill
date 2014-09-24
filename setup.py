from setuptools import setup, find_packages

setup(
    name='seed_drill',
    version='0.1.0',
    url='https://github.com/kostajh/seed_drill',
    description=(
        'Simplify logging times in Harvest from Taskwarrior'
    ),
    author='Kosta Harlan',
    author_email='kosta@kostaharlan.net',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        "taskw",
        "requests",
        "pyaml"
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sd = seed_drill:cmdline'
        ],
    },
)
