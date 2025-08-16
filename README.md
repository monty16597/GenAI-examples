# langchain-examples
This repository contains examples and tutorials for using the LangChain library, which is designed to facilitate the development of applications powered by language models. The examples cover a range of use cases of features provided by LangChain, including prompt engineering, chains, agents, memory, and more.

## Setup
- To set up the environment for running the examples, follow these steps:
```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
- Install jupyter notebook if you want to run the examples interactively:
```bash
pip install jupyter
```
- Add `.env` file. Refer `.env.sample` file. Add your Google API key:
```bash
cp .env.sample .env
```
- Run the following command to start the Jupyter notebook:
```bash
jupyter notebook
```