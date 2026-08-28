from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="crude-engine",
    version="2.9.0",
    packages=find_packages(),
    package_data={
        "crude_engine": [
            "engine/*.yaml",
            "drivers/*.yaml",
            "schemas/*.yaml",
            "wire/*.yaml",
            "wire/**/*.yaml",
        ],
    },
    description="YAML-driven declarative schema engine for network device management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Adam Rickards",
    author_email="adam_rickards@hotmail.com",
    url="https://github.com/AdamRickards/crude-engine",
    install_requires=[
        "netmiko>=3.3.0",
        "pysnmp>=4.4.12",
        "requests>=2.20.0",
        "pyyaml>=5.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
