from setuptools import setup, find_packages
import MarkovTextGenerator

setup(
    name="MarkovTextGenerator",
    version=MarkovTextGenerator.__version__,
    author=MarkovTextGenerator.__author__,
    url="https://github.com/NyashniyVladya/MarkovTextGenerator",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: GNU GENERAL PUBLIC LICENSE"
    ],
    install_requires=[
        "shutil"
    ],
    keywords=(
        "vladya markovgenerator markov_generator markov_chain "
        "MarkovTextGenerator"
    ),
    description="Generator of pseudo-random text, using Markov chains.",
    long_description=(
        "Генератор псевдорандомного текста, посредством цепей Маркова."
    )
)
