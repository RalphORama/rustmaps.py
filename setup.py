"""Setuptools module for PyPi package."""

from setuptools import setup, find_packages
# from rustmaps import __version__
import pathlib

__version__ = '0.1.0'
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="rustmaps.py",
    version=f"{__version__}",
    description="A Python 3 wrapper for the rustmaps.com HTTP REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RalphORama/rustmaps.py",
    author="Ralph Drake",
    author_email="pypi@ralphdrake.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="requests api development",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    # py_modules=["rustmaps"],
    python_requires=">=3.8, <4",
    install_requires=["requests"],
    project_urls={
        "Bug Reports": "https://github.com/RalphORama/rustmaps.py/issues",
        "Source": "https://github.com/RalphORama/rustmaps.py/",
    },
)
