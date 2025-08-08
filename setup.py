from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="log-whisperer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An AI log analyzer with chat interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/log-whisperer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debugging",
        "Topic :: System :: Logging",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.1",
        "langchain-core>=0.1.0",
        "pyyaml>=6.0",
        "rich>=13.0.0",
        "prompt-toolkit>=3.0.0",
        "chromadb>=0.4.0",
        "sentence-transformers>=2.2.0",
        "tiktoken>=0.5.0",
        "faiss-cpu>=1.7.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "openai": ["langchain-openai"],
        "anthropic": ["langchain-anthropic"],
        "google": ["langchain-google-genai"],
        "azure": ["langchain-openai"],
        "cohere": ["langchain-cohere"],
        "huggingface": ["langchain-huggingface"],
        "ollama": ["langchain-ollama"],
    },
    entry_points={
        "console_scripts": [
            "log-whisperer=log_whisperer.cli:main",
        ],
    },
)
