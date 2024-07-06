## This notebook contains Evaluation of Granite (granite-code:8b-instruct-q4_0) model .
#### Approach followed while evaluation
* There are two tables in database
* 20 questions are generated using Chatgpt. Out of which 10-Simple , 5-medium ,5-complex questions along with sql queries. All these are related to data present in two tables . Important: In production , we will not expose real  data , just schema is provided . But here we have to manually check the generated queries results. For our simplicity , we inserted some data in tables .
* Granite model run on 20 queries. It generates the sql queries.
* LLM generated queries , Ground-Truth (Actual queries cross checked by human) are manually run on mysql to see the generated results.
* Out of 20 questions , 2 were wrong .

