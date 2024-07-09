from langchain_community.llms import Ollama
from operator import itemgetter
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
import sqlparse

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

app = FastAPI()

# ----------------------------------------------------------------------------Access model via ollama----------------------------------------------------------
# 20b 4bit quantized
# llm = Ollama(base_url="http://172.27.222.2:11434",
#     model="granite-code:20b-instruct-q4_0"
# ) 

#This is 8b 4bit model
#Load model . Model is running on server deployed using ollama .
llm = Ollama(base_url="http://172.27.222.2:11434",
    model="granite-code:8b-instruct-q4_0" , temperature=0
) 


# ollama set up at your local-system
# llm = Ollama(base_url="http://localhost:11434",
#     model="granite-code:8b-instruct-q4_0"
# ) 


# Establish connection with mysql
mysql_uri = 'mysql+mysqlconnector://root@localhost:3306/inventory_db'
db = SQLDatabase.from_uri(mysql_uri)

template = """
<|begin_of_text|><|start_header_id|>user<|end_header_id|>
Generate a SQL query to answer this question: `{question}`
DDL statement:
CREATE TABLE backorder_data (
    Type VARCHAR(50),
    Start,
    End,
    Location Name VARCHAR(50),
    Buyer VARCHAR(50),
    Supplier Id INT,
    Supplier VARCHAR(100),
    Activity Code VARCHAR(20),
    Velocity Code CHAR(1),
    Product Code VARCHAR(20),
    Product Description VARCHAR(200),
    LT INT,
    [5/24/2024] INT,
    [6/1/2024] INT,
    [7/1/2024] INT,
    [8/1/2024] INT,
    [9/1/2024] INT,
    [10/1/2024] INT,
    [11/1/2024] INT,
    [12/1/2024] INT,
    [1/1/2025] INT,
    [2/1/2025] INT,
    [3/1/2025] INT,
    [4/1/2025] INT
);

Metadata:
Type: Category of data (e.g., "Backorder")
Start: Start date of the backorder period
End: End date of the backorder period
Location Name: Location of the backorder (e.g., "TN")
Buyer: Name of the buyer responsible for the backorder
Supplier Id: Unique identifier for the supplier
Supplier: Name of the supplier
Activity Code: Code indicating the activity status (e.g., "A -Active")
Velocity Code: Single character code related to backorder velocity
Product Code: Unique identifier for the product
Product Description: Brief description of the product
LT: Lead time (in days)
[Date columns]: Backorder quantities for each month from May 2024 to April 2025

Examples:
1. Total backorder quantity for May 2024:
   SELECT SUM([5/24/2024]) AS total_backorder FROM backorder_data WHERE Type = 'Backorder';

2. List all products supplied by a specific supplier:
   SELECT DISTINCT Product Code, Product Description FROM backorder_data WHERE Supplier = 'JIWANRAM SHEODUTTRAI INDUSTRIES PVT. LTD';

3. Count of products with different sizes:
   SELECT 
     SUM(CASE WHEN Product Code LIKE '%L' AND Product_Code NOT LIKE '%XL' THEN 1 ELSE 0 END) AS Large,
     SUM(CASE WHEN Product Code LIKE '%XL' THEN 1 ELSE 0 END) AS Extra_Large,
     SUM(CASE WHEN Product Code LIKE '%2X' THEN 1 ELSE 0 END) AS Double_Extra_Large
   FROM backorder_data;

4. Total backorder for a specific product across all months:
   SELECT Product Code, 
     SUM([5/24/2024] + [6/1/2024] + [7/1/2024] + [8/1/2024] + [9/1/2024] + [10/1/2024] + 
         [11/1/2024] + [12/1/2024] + [1/1/2025] + [2/1/2025] + [3/1/2025] + [4/1/2025]) AS Total_Backorder
   FROM backorder_data
   WHERE Product Code = 'RWG3700XL'
   GROUP BY Product Code;

5. Products with lead time greater than average:
   SELECT Product Code, LT
   FROM backorder_data
   WHERE LT > (SELECT AVG(LT) FROM backorder_data);

Generate a SQL query that best answers the question: `{question}`
<|eot_id|><|start_header_id|>assistant<|end_header_id|>

```sql

"""

from langchain.prompts import PromptTemplate
prompt = PromptTemplate.from_template(template=template)
chain = prompt | llm 

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
        response = chain.invoke(question)
        
        return QueryResponse(question=question, query=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#----------------------------------------API for Response from mysql ----------------------------------------------------------

class QueryRequest(BaseModel):
    question: str

class QueryAnswer(BaseModel):
    question: str
    answer: str

@app.post("/generate_response")
async def ask_question(request: QueryRequest) -> Any:
    question = request.question
    try:   
        execute_query = QuerySQLDataBaseTool(db=db)
        chain =  prompt | llm  | execute_query
        result = chain.invoke({'question':question})
        return QueryResponse(question=question, query=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)