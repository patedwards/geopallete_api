from setuptools import setup

setup(
    name="palettemap",
    version="0.1",
    install_requires=[
        "flask",
        "numpy",
        "sklearn",
        "matplotlib",
        "pillow",
        "flask_cors",
        "pyopenssl",
        "gunicorn"
    ],
)