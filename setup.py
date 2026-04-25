from setuptools import setup, find_packages

setup(
    name="kubeinspector",
    version="1.0.0",
    description="🏴☠️ Pirate-themed Kubernetes YAML Inspector & Auto-Fixer",
    author="Captain",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
        "jinja2>=3.1.0",
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "kubeinspector=kubeinspector.main:main",
        ],
    },
    python_requires=">=3.10",
)
