# HokieEATS

```
Please make sure to use your own keys in .env file
```

### You can access the Deployed Project Here: https://hokieeats.study/

## Inspiration
Virginia Tech has a student body that very often wants food from different cuisines but has no efficient means to decide on the best restaurant choices. We envisioned a system whereby any student can quickly find a perfect meal based on his or her preferences and diet requirements. This led to the development of HokieEATS, a conversational knowledge-based chatbot with a rather friendly user interface-something very easy for students to find great places to eat around campus.

## What it does
HokieEATS is a bot that suggests restaurants based on data input by the user. Food locations have been scraped from Google Maps; the restaurant information, such as the type of cuisine, calories, price range, diet, allergic options, and many others, was gathered and inserted into the MongoDB database. When users utilize the chatbot, MongoDB queries are created concerning the user preferences, semantic searches are done to present the results of the best-matching restaurant option. Results are displayed in an appealing, conversational format.
## How we built it

The core of HokieEATS involves the usage of the **Microservices Architecture** to tear down the system into independent services. Each of these is focused on one particular function. This kind of modularity not only made development more manageable, but it also made scaling and deployment of each component independently much easier. Following is how we did the building of various aspects of the project:

1. **Frontend**:
Streamlit was used to construct a lightweight but responsive user interface. In this way, we would easily create a user-friendly frontend that users would use to interact with the chatbot. There is an interface with a chat window from which a user can ask questions about restaurants visually, providing responses with personalized suggestions through HokieEATS.
The **Streamlit** framework allowed rapid prototyping and testing, making it easy to tweak the user experience without lengthy development cycles.

2. **Backend**:
HokieEATS has been written primarily in **Python**; it's the driving force of the business logic behind the processing of user queries and fetching data about restaurants. We chose to host the backend on **Azure Functions** for handling requests with its serverless architecture that reduces operational overhead.
It takes user inputs, generates MongoDB queries using an LLM-powered backend with **LangChain** and **Azure OpenAI**, and retrieves the data relevant to the user. After retrieval, the data is processed and the results are returned to the user via the chatbot interface.

3. **Data Collection**:
We developed and implemented a custom **web scraper** to scrape restaurants from **Google Maps**. This web scraper fetches critical information like the names of places, types of food, price ranges of dishes, menu items, dietary options, and even ingredients used in certain dishes. We stored this information in **MongoDB**, updating and querying in real time.
This scraper runs periodically to keep the data up-to-date, adding and updating entries within the MongoDB database. It ensures that the latest restaurants will always be available to the user, hence improving the overall user experience.

4. **Database**:
All information about the restaurants was housed in a **MongoDB** database. We wanted to handle unstructured data, such as those related to restaurants, efficiently, and most of the entries have big variations among them-for example, different menu format or types of cuisines served.
- The chatbot forms a dynamic MongoDB query language- MQL statement based on the query and executes it to retrieve information stored in the database.

5. **Vector Search with FAISS**:
In **FAISS**, we cache relevant data retrieved in this fast in-memory vector store, which supports efficient similarity searches, that were of essence while carrying out semantic searches based on the input given by the user.
With respect to that, by storing the vector representations of the restaurant data, we are then able to find the closest possible matches to any user query so that the suggestions presented by a chatbot are as close to what is being asked for.

6. **Language Model and Query Generation**:
The main components of our language models were **LangChain** and **Azure OpenAI**. LangChain provided a structured way of creating pipelines in generating natural language responses based on queries that a user may have.
It is the responsibility of LangChain to summarize the chat history after a question has been submitted by the user, develop a MongoDB query, and format it for execution. This query essentially readies our database for pulling relevant restaurant information through the semantic analyzer.
- We then built two **Retrieval-Augmented Generation (RAG) models:
- **RAG 1 uses these inputs provided by the user to build MongoDB queries. It also considers the preferences set by the user through this application and conversation history, if any.
- **RAG 2** takes the results returned from MongoDB and creates a nicely formatted response back to the user, filtering through the data to ensure that it's what the user requested.

7. **Deployments and Scalability**:

By choosing **Azure Functions** for the backend, we made sure it would scale with demand. This serverless design means the back-end can handle more requests than ever before, without any manual intervention or managing of the infrastructure.

The microservices architecture is modularly designed, meaning that each part of the service, such as the web scraper, the chatbot logic, and the database querying, can be deployed and scaled autonomously where needed. This flexibility will allow us to introduce new features or improvements without causing any down time or interruptions in the service.


8. **Security and Privacy:**

Major was the issue of user privacy. Interactions between frontend and backend were all over HTTPS. Sensitive data such as user preference was stored in a secure database, and we made sure none of the PII was being collected or stored.

All of the backend services' authentications have been done through **Azure's Identity Management** to ensure that only authorized services have access to sensitive resources - such as the MongoDB instance, or even the LangChain pipeline.

We carefully selected technologies and architectures that might become the backbone to support our goals; thus, HokieEATS was developed as a robust, scalable platform that should provide exact real-time recommendations about restaurants matched for the needs of each user. Challenges We Ran Into We faced several hiccups during development, mainly when deploying our backend on Azure Functions. Initial problems with JSON query formatting in MongoDB delayed the processing of user queries. We have, however, managed to resolve them by refining the way we handle schema and ensuring proper query generation with LangChain and Azure OpenAI models. ## Accomplishments that we're proud of We are proud to develop a functional food recommendation system that will enhance the dining experience of the students at Virginia Tech. By integrating multiple technologies such as LangChain, MongoDB, FAISS, and Azure Functions, we have been able to build a scalable solution for accurate real-time results. ## What we learned In this project, we have learned how to scrape and manage large datasets more efficiently, generate dynamic MongoDB queries using LLMs, and implement seamless connections between the chatbot frontend and backend services. Equally valuable was the experience of knowing how to troubleshoot challenges in cloud deployment on Azure. ## What's next for HokieEATS We will improve HokieEATS by building on the dataset of restaurants and cuisines that surround Virginia Tech. We also plan to implement more conversational improvements into the chatbot, which would make it more personal and intuitive for the users. In the future, we can build this into a system displaying restaurants in real time with user reviews to further filter recommendations.
