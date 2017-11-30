from setuptools import setup, find_packages
from MarkovTextGenerator import markov_text_generator

setup(
    name="MarkovTextGenerator",
    version=markov_text_generator.__version__,
    author=markov_text_generator.__author__,
    url="https://github.com/NyashniyVladya/MarkovTextGenerator",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3.6"
    ],
    keywords="vladya markovgenerator markov_generator markov_chain"
)
