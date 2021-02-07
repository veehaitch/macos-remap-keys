import setuptools
from pathlib import Path
import json

setuptools.setup(
    name="macos-remap-keys",
    version="0.1",
    author="Vincent Haupert",
    author_email="mail@vincent-haupert.de",
    url="https://github.com/veehaitch/macos-remap-keys",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.0",
    install_requires=Path("requirements.txt").read_text().splitlines(),
    scripts=["remap.py"],
)
