from setuptools import setup, find_packages

setup(
    name="openfisca-us-data",
    version="0.1.4",
    description=(
        "A Python package to manage OpenFisca-US-compatible microdata"
    ),
    url="http://github.com/PolicyEngine/openfisca-us-data",
    author="Nikhil Woodruff",
    author_email="nikhil.woodruff@outlook.com",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "pathlib",
        "tqdm",
        "tables",
        "h5py",
        "synthimpute",
        "pytest",
        "pytest-dependency",
        "requests",
    ],
    extras_require={
        "dev": [
            "autopep8",
            "black",
            "setuptools",
            "wheel",
            "openfisca-us",
            "pyyaml",
        ],
    },
    entry_points={
        "console_scripts": ["openfisca-us-data=openfisca_us_data.cli:main"],
    },
    include_package_data=True,
    package_data={'': ['openfisca_us_data/datasets/ce/*.yaml']},
)
