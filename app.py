from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
import sqlparse

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

app = FastAPI()


# 20b 4bit quantized
# llm = Ollama(base_url="http://172.27.222.2:11434",
#     model="granite-code:20b-instruct-q4_0"
# ) 

# This is 8b 4bit model
# Load model . Model is running on server deployed using ollama .
llm = Ollama(base_url="http://172.27.222.2:11434",
    model="granite-code:8b-instruct-q4_0"
) 



# llm = Ollama(base_url="http://localhost:11434",
#     model="granite-code:8b-instruct-q4_0"
# ) 



# Establish connection with mysql
mysql_uri = 'mysql+mysqlconnector://root@localhost:3306/test'
db = SQLDatabase.from_uri(mysql_uri)

# This chain generates SQL queries for the given database.
write_query = create_sql_query_chain(llm, db)



#------------------------------------------------API for generating SQL query----------------------------------
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    query: str

@app.post("/generate_sql")
async def ask_question(request: QueryRequest) -> Any:
    question = request.question
    try:
        response = write_query.invoke({'question':question})
        response = sqlparse.format(response)
        return QueryResponse(question=question, query=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#----------------------------------------API for RAG ----------------------------------------------------------

class QueryRequest(BaseModel):
    question: str

class QueryAnswer(BaseModel):
    question: str
    answer: str

@app.post("/generate_answer")
async def ask_query(request: QueryRequest) -> Any:
    question = request.question
    try:
        answer_prompt = PromptTemplate.from_template(
                    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

                Question: {question}
                SQL Query: {query}
                SQL Result: {result}
                Answer: """
                )
        execute_query = QuerySQLDataBaseTool(db=db)
        answer = answer_prompt | llm | StrOutputParser()
        chain = (
            RunnablePassthrough.assign(query=write_query).assign(
                result=itemgetter("query") | execute_query
            )
            | answer
        )
        response = chain.invoke({"question":  question})
        return QueryAnswer(question=question, answer=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)