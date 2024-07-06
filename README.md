# Chat with Database
This repository contains the code for Chat with Database.


### Set up ollama on your system (Step-1)
Linux system
* Command --> curl -fsSL https://ollama.com/install.sh | sh
* Website --> https://ollama.com/download
### Setup LLM (Step-2)
* Command --> ollama pull granite-code:8b-instruct-q4_0
* Website --> https://ollama.com/library/granite-code:8b-instruct-q4_0
* We are using 8b 4bit quantized model . Model is present in 3b , 8b, 20b,34b variants . Base and quantized versions are present. You can use depending on the system configuration.


app.py is the API . It has two functionalities:
* First , it takes user question and return SQL query
* Second, it takes user question and return natural answer .

### How to use it 
###### Setup Python Environment
To get started with this project, follow these steps to create and activate a Python environment using `conda`, and install the required dependencies.

###### Create a Conda Environment
First, create a new conda environment with Python 3.10:

```bash
conda create --name name_of_environ python==3.10
conda activate name_of_environ
```
* Install requirements
```bash
pip install -r requirements.txt
```
* If ollama is not setup in your system , follow step-1 and step-2 given above.
* Setup mysql and access the database.
* Finally Run:
```bash
python app.py
```

#### API contains two end  points
* generate_sql :  Which is used to generate sql query given question from the user.
* generate_answer : Which is used to generate exact answer given question from the user. 
