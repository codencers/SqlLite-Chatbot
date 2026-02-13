import streamlit as st
from pathlib import Path
import sqlite3
from sqlalchemy import create_engine

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_groq import ChatGroq


st.set_page_config(page_title="LangChain: Chat with SQL DB")
st.title("LangChain: Chat with SQL DB")

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = [
    "Use SQLLite3 DataBase - Student.db",
    "Connect to your SQL Database"
]

selected_opt = st.sidebar.radio(
    label="Choose the DB which you want to chat",
    options=radio_opt
)

if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL

    mysql_host = st.sidebar.text_input("Provide My SQL Host")
    mysql_user = st.sidebar.text_input("MYSQL User")
    mysql_password = st.sidebar.text_input("MYSQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database")

else:
    db_uri = LOCALDB


api_key = st.sidebar.text_input(
    label="Enter your Groq API Key",
    type="password"
)

if not api_key:
    st.info("Please enter your Groq API Key")
    st.stop()


llm = ChatGroq(
    api_key=api_key,
    model_name="Gemma2-9b-It",
    streaming=True
)


@st.cache_resource(ttl="2h")
def configure_db(
    db_uri,
    mysql_host=None,
    mysql_user=None,
    mysql_password=None,
    mysql_db=None
):

    if db_uri == LOCALDB:
        dbfilepath = (Path(__file__).parent / "student.db").absolute()

        creator = lambda: sqlite3.connect(
            f"file:{dbfilepath}?mode=ro",
            uri=True
        )

        engine = create_engine("sqlite://", creator=creator)
        return SQLDatabase(engine)

    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()

        engine = create_engine(
            f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"
        )

        return SQLDatabase(engine)


if db_uri == MYSQL:
    db = configure_db(
        db_uri,
        mysql_host,
        mysql_user,
        mysql_password,
        mysql_db
    )
else:
    db = configure_db(db_uri)


toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True
)


if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


user_query = st.chat_input(
    placeholder="Ask anything from the database"
)

if user_query:
    st.session_state.messages.append(
        {"role": "user", "content": user_query}
    )
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):

        response = agent.run(user_query)

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )

        st.write(response)
