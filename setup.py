import io
from setuptools import setup, find_packages

__version__ = "0.7.1"


def get_requirements(file_name):
    requirements = []
    for line in io.open(file_name):
        line = line.strip()
        if not line or "://" in line or line.startswith("#"):
            continue
        requirements.append(line)
    return requirements


def get_long_description():
    return io.open("README.md", encoding="utf-8").read()


setup(
    name="FastAPI-REST-JSONAPI",
    version=__version__,
    description="FastAPI-REST-JSONAPI",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Zenor27/fastapi-rest-jsonapi",
    author="Zenor27",
    author_email="antoine.montes@epita.fr",
    license="MIT",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: FastAPI",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="rest json api jsonapi fastapi database sql",
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    platforms="any",
    include_package_data=True,
    install_requires=get_requirements("requirements.txt"),
    tests_require=["pytest"],
)
