from setuptools import setup

setup(
    name='fytw',
    version=0.1,
    py_modules=['fytw'],
    install_requires=[
        'Click',
        'Flask',
        'Flask-WTF',
        'alembic',
        'flask-admin',
    ],
    entry_points='''
        [console_scripts]
        fytw=fytw:cli
    ''',
)
