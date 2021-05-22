from distutils.core import setup

TEST_REQUIREMENTS = [
    "pytest==6.2",
    "pytest-cov==2.12",
]

setup(
    name='dateinfer',
    version='1.0.0',
    description='Infers date format from examples',
    long_description="""
    Uses a series of pattern matching and rewriting rules
    to compute a "best guess" datetime.strptime format string give
    a list of example date strings.""",
    author='Jeffrey Starr',
    author_email='jeffrey.starr@ztoztechnologies.com',
    url='https://github.com/leferrad/dateinfer',
    packages=['dateinfer'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    extra_require={
        "tests": TEST_REQUIREMENTS
    }
)
