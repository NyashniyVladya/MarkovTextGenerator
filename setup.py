from setuptools import setup, find_packages
from MarkovTextGenerator import markov_text_generator

with open("README.md", "rb") as readmeFile:
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
        keywords="vladya markovgenerator markov_generator markov_chain",
        description="Generator of pseudo-random text, using Markov chains.",
        long_description=readmeFile.read().decode("utf-8", "ignore")
    )
