from setuptools import setup, find_packages

setup(
    name="octoplug",
    version="0.1",
    description="OctoPyPlug BAC2",
    author="Varga Peter",
    author_email="varga.pter91@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["setuptools"],
)
