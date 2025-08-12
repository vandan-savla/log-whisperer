from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="log-whisperer",
    version="0.1.0",
    author="Vandan Savla",
    author_email="vsavla21@gmail.com",
    description="An AI log analyzer with chat interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vandan-savla/log-whisperer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debugging",
        "Topic :: System :: Logging",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click",
        "langchain",
        "langchain-community",
        "langchain-core",
        "langchain-huggingface",
        "pyyaml",
        "rich",
        "prompt-toolkit",
        "chromadb",
        "sentence-transformers",
        "tiktoken",
        "faiss-cpu",
        "numpy",
        
    ],
    extras_require={
        "openai": ["langchain-openai"],
        "anthropic": ["langchain-anthropic"],
        "google": ["langchain-google-genai"],
        "azure": ["langchain-openai"],

    },
    entry_points={
        "console_scripts": [
            "log-whisperer=log_whisperer.cli:main",
        ],
    },
)
