from setuptools import setup, find_packages

__version__ = "0.0.1"


def get_requirements(file_name):
    with open(file_name) as f:
        return f.read().splitlines()


setup(
    name="FastAPI-REST-JSONAPI",
    version=__version__,
    description="FastAPI-REST-JSONAPI",
    url="https://github.com/Zenor27/fastapi-rest-jsonapi",
    author="Zenor27",
    author_email="antoine.montes@epita.fr",
    license="MIT",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: FastAPI",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT LicenseLicense :: OSI Approved :: MIT License",
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
    install_requires=get_requirements("requirements.txt"),
    tests_require=["pytest"],
)
