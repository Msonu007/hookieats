import azure.functions as func
import logging
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
import pymongo
import urllib
from pymongo import MongoClient
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.chat_history import BaseChatMessageHistory
import json
import logging
from collections import defaultdict
from langchain_core.output_parsers import JsonOutputParser
import re
import pydantic
load_dotenv()

class MQL(pydantic.BaseModel):
    query: str = Field(description="The MongoDB query to be added to pymongo")

# Azure Function setup
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)



if "OPENAI_API_KEY" not in os.environ:
    openai_api_key = os.environ["API_KEY"]
    os.environ["OPENAI_API_KEY"] = openai_api_key

# MongoDB connection
username = os.environ["USER_NAME"]
password = os.environ["PASS"]
escaped_username = urllib.parse.quote_plus(username)
escaped_password = urllib.parse.quote_plus(password)
client = MongoClient(f"mongodb+srv://{escaped_username}:{escaped_password}@datavthacks.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000&tlsAllowInvalidCertificates=true")

# Function to pull data from MongoDB
def pull_from_db(query):
    db = client['newdb']
    collection = db['newCollection']
    client.admin.command("ping")
    # out_ = collection.find(query)
    out_ = db.newCollection.aggregate(query)
    return list(out_)

# Function to retrieve the schema of the MongoDB collection
def get_schema(name):
    collection = client["newdb"][name]
    schema = defaultdict(set)
    for doc in collection.find():
        for key, value in doc.items():
            schema[key].add(type(value).__name__)

    schema = {k: list(v) for k, v in schema.items()}
    return json.dumps(schema, indent=2)

# Function to generate the MongoDB query using LangChain
def generate_mongo_query(user_message, chat_history):

    schema1 = get_schema("newCollection")
    schema2 = get_schema("Restaurants")
    # Define the prompt for generating MongoDB query
    mongo_prompt_template = f"""
    You are a MongoDB MQL assistant. 
    ```
    1. Collection Name: "newCollection" with Schema: 
    ```
    {schema1}
    ```

    ```

    ```
    2. Collection Name: "Restaurants" with Schema: 
    ```
    {schema2}
    ```
    
    ```
    ```
    Chat history of the old conversations are as follows:
    {chat_history}
    Summarize the chat history and generate a MongoDB query based on the user message.
    ```
I have two MongoDB collections: newCollections and Restaurants. Both collections contain a field called restaurant_id. I want to create a MongoDB query that performs an inner join between these two collections on the restaurant_id field. Additionally, the query should filter the results based on a user-specified restaurant_id.

Please generate a MongoDB aggregation pipeline that accomplishes the following:

Joins the newCollections collection with the Restaurants collection on restaurant_id.
Filters the records based on a user's prefererences
Returns the matching documents.

Rules:
1. Make sure to have double quotes around the field names.
2. Return the appropriate MongoDB query in VALID JSON Output in given format for the following user request:
    {user_message}
3. Only give me the attributes so that I can pass them to pymongo instance, Do Not use "user_specified_id" in the query.
4. Do not give me python code, only the pipeline query.
5. Do not assume and use any  field names or values in the query which is not there in the schema.
6. [STRICT] Use regex to match all the Columns with the user requirements, even if one word is present you can consider it as a match. 
7. [STRICT] Limit the number of records to 10.
8. [STRICT] Do not use Location for filtering in the query.
    """

    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    parser = JsonOutputParser(pydantic_object=MQL)

    prompt = PromptTemplate(
    template="{mongo_prompt_template}.\n{format_instructions}\n{query}\n",
    input_variables=["query","mongo_prompt_template"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    logging.info(f"Prompt: {prompt}")
    #logging.info(f"Mongo_prompt_template: {mongo_prompt_template}")
    chain = prompt | model | parser

    chainresponse= chain.invoke({"query": user_message, "mongo_prompt_template": mongo_prompt_template})
    logging.info(f"Before MongoDB query: {chainresponse} type: {type(chainresponse)}")
    chainresponse = chainresponse['query']
    


    # structured_llm = model.with_structured_output(MQL)
    # response = structured_llm.invoke(mongo_prompt_template)
    # query_str = response.query.replace("'", '"')
    # query_str = re.sub(r'(\$\w+)', r'"\1"', query_str)
    # logging.info(f"Generated MongoDB query: {query_str} type: {type(query_str)}")
    # mongo_query = json.loads(query_str)
    return chainresponse


# Function to generate response based on retrieved data and user message
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

# Function to generate response based on retrieved data and user message
def generate_response_with_data(user_message, retrieved_data):
    context = f"The following data was retrieved from the database: {retrieved_data}"

    # Define the prompt for generating a response based on the data and user message
    response_prompt_template = f"""
    You are a helpful assistant named "Tomato" that uses provided data to answer questions.
    Context: {context}
    User message: {user_message}
    Rules:
    1. Only if the context is empty, Let me know that Tomato is sorry as it was not able to find any good restaurants, ask for the user's preference so that you can provide the best restaurants.
    2. If the user did not ask any question, Tomato should ask the user if they would like to know about the best restaurants .
    3. [STRICT] If the user asks about any restaurants nearby/"near me", Tomato should provide the user with all the available options based on the retrieved data. The response should be intelligent such that there is no redundancy.
    4. If the user talks about something else, Tomato should be funny and try to divert the topic by asking the user if they would like to know about the best restaurants.
    5. If the context was not empty and it returned some data, Tomato should provide the user with the top restaurants based on the retrieved data and give their details which would be useful for the user.
    6. You dont have to say Sorry if you gave some data to the user.
    7. If you answer the user's question, you DONT need to ask the user if they would like to know about the best restaurants.
    8. Dont talk about diet options and Price Rank in the response.
    9. If the user did not give any specific preference, you can give top rated restaurant details.
    10.[STRICT] Dont use bullet points (-) in the response, but you dont have to restrict to 1 record if the dataset have more records.
    11. Make sure not to deviate from the topic/foods asked in the user question.
    12. [STRICT] If you cannot find any restaurants, Tomato should provide the user with all the available options based on the retrieved data.
    13. You dont have to be Sorry if the context is not empty and you have some data to provide to the user.
    14. [STRICT] Do not show "Cuisine Type" in the response, Only show "Restaurant Name","Location","Dishes" always.
    15. [STRICT] send the response so that i can format it in html orderlists.
    """

    response_prompt = PromptTemplate(
        input_variables=["user_message"],
        template=response_prompt_template
    )

    # Initialize the model
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    result = model.invoke(response_prompt_template)
    return result.content

def summarizer(user_message):
    # Define the prompt for summarizing the user message
    summarizer_prompt_template = f"""
    You are a summarizer assistant that summarizes the user message.
    User message: {user_message}
    Summarize the user message in a single sentence without loss of context.
    """

    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    response = model.invoke(summarizer_prompt_template)
    return response.content

@app.route(route="yourtomato")
def yourtomato(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f"Request : {req.get_json()}")
    try:
        req_body = req.get_json()
        user_message = req_body['user_message']
        chat_history = req_body['chat_history']
        logging.info(f"User message: {user_message}")
        logging.info(f"Chat history: {chat_history}")
        chat_history = summarizer(chat_history)
        # Generate MongoDB query using LangChain
        mongo_query = generate_mongo_query(user_message,chat_history)
        
        # # Retrieve data from MongoDB based on the generated query
        retrieved_data = pull_from_db(mongo_query)
        logging.info(f"Retrieved data: {retrieved_data}")
        # # Generate the final response with data
        llm_response = generate_response_with_data(user_message, retrieved_data)
        response_json = {
            "response": llm_response
        }
        logging.info(f"Response: {llm_response}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return func.HttpResponse(
            f"An error occurred: {str(e)}", status_code=500
    )
    if user_message:
        return func.HttpResponse(json.dumps(response_json), status_code=200)
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass 'user_message' in the request body for a personalized response.",
            status_code=404
        )