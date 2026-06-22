"""Compatibility shim for older pip editable installs."""

from setuptools import find_packages, setup


setup(
    name="pokerbench-ng",
    version="0.1.0",
    description="Clean-room local-first benchmark for AI poker agents",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.9",
    entry_points={"console_scripts": ["pokerbench-ng=pokerbench_ng.cli:main"]},
)
