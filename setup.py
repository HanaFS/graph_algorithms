from setuptools import setup, find_packages

setup(
    name="graph_algorithms",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        # Thêm các thư viện cần thiết ở đây
    ],
    python_requires=">=3.8",
)
