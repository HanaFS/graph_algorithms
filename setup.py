from setuptools import setup, find_packages

setup(
    name="graph_algorithms",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "matplotlib>=3.7.0",
        "networkx>=3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=21.0",
            "pylint>=2.12",
            "flake8>=4.0",
        ],
    },
    python_requires=">=3.9",
)
