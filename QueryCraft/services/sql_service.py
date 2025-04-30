from utils.database_utils import is_database_empty, load_sql_data, extract_ddl_from_db
from services.model_invoker import CohereInvoker, ClaudeInvoker, OpenAIInvoker, ModelInvoker, get_model_invoker
import sqlite3
import sys
import os
import logging
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
# Resolve the absolute path of the SQL file
sql_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_file", "SampleData.sql"))  # Correct path

# Initialize BedrockInvoker

def load_data_into_database(db_name):
    # Check if the database is empty and load data if necessary
    if is_database_empty(db_name):
        logging.info("db_name: %s", db_name)
        logging.info("sql_file_path: %s", sql_file_path)    
        load_sql_data(db_name, sql_file_path)
        database_status = "Database was empty. Data has been loaded."
        logging.info("Database was empty. Data has been loaded.")
    else:
        database_status = "Database is already populated. Skipping data load."
        logging.info("Database is already populated. Skipping data load.")
        # return load_sql_data(db_name, sql_file_path=sql_file_path)

    return {
        "database_status": database_status,
        "db_name": db_name,     
        "sql_file_path": sql_file_path
    }


def prompt_template(ddl_schema, additional_text):
    """
    Generates a prompt for the LLM to understand the DDL schema and generate SQL queries.
    """
    prompt_template = (
       "As an expert SQL analyst, examine the following DDL schema:\n\n"
        "{ddl_schema}\n\n"
        "Based on this schema, generate an optimized SQL query for SQLite3 that addresses the following request:\n\n"
        "{additional_text}\n\n"
        "Instructions:\n"
        "1. Analyze the schema to identify tables, columns, data types, and constraints (PRIMARY KEY, FOREIGN KEY).\n"
        "2. Determine table relationships.\n"
        "3. Construct a SQL query that:\n"
        "   - Addresses the specific request\n"
        "   - Uses only columns present in the provided schema\n"
        "   - Is optimized for performance\n"
        "   - Follows SQLite3 syntax\n\n"
        "Provide only the SQL query as your response, without any additional explanation."
    )
    return {"prompt": prompt_template.format(ddl_schema=ddl_schema, additional_text=additional_text),
            "temperature": 0.1,
            "stop_sequences": []}

def process_sql_request(prompt: str, db_name: str, model_type: str) -> dict:
    """
    Processes the SQL request: checks database, invokes the selected model, and runs the SQL query.
    """
    max_retries = 2  # Number of retries for model invocation

    # Extract the DDL from the database
    ddl_statements = extract_ddl_from_db(db_name)
    logging.info(f"Extracted DDL statements from the database: {ddl_statements}")

    # Get the appropriate model invoker
    invoker = get_model_invoker(model_type)

    # Retry mechanism for model invocation
    response = None
    prompt_text = prompt_template(ddl_statements, prompt)["prompt"]
    for attempt in range(max_retries + 1):
        try:
            logging.info(f"Attempting to invoke {model_type} model (Attempt {attempt + 1}/{max_retries + 1})... Prompt: {prompt_text}")
            response = invoker.invoke(prompt_text, max_tokens=512, temperature=0.1, stop_sequences=[])
            if response:  # Exit the retry loop if a valid response is received
                logging.info(f"{model_type.capitalize()} model invocation successful. Response: {response}")
                break
        except Exception as e:
            if attempt < max_retries:
                logging.warning(f"Retrying {model_type} model invocation (Attempt {attempt + 1}/{max_retries})...")
                time.sleep(2)  # Add a delay between retries
            else:
                logging.error(f"{model_type.capitalize()} Invocation Failed: {e}")
                raise Exception(f"{model_type.capitalize()} Invocation Failed: {e}")

    # Check if the response is None
    if response is None:
        logging.error(f"{model_type.capitalize()} returned no response.")
        raise Exception(f"{model_type.capitalize()} returned no response.")

    # Extract the SQL query from the response
    if "```sql" in response:
        sql_query = response.split("```sql")[1].split("```")[0].strip().strip("\n")
    else:
        sql_query = response.strip().strip("\n")
    logging.info(f"Generated SQL query: {sql_query}")

    # Run the SQL query on the database
    results = run_sql_query(db_name, sql_query)
    logging.info(f"SQL query executed successfully. Retrieved {len(results)} rows.")

    return {"generated_sql": sql_query, "results": results}

   
def run_sql_query(db_name, query):
    """
    Runs a SQL query on the specified SQLite3 database.
    """
    try:
        logging.info(f"Connecting to the database '{db_name}' to execute the query.")
        # Connect to the SQLite3 database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Execute the SQL query
        logging.info(f"Executing SQL query: {query}")
        cursor.execute(query)

        # Fetch all results
        results = cursor.fetchall()
        logging.info(f"Query executed successfully. Retrieved {len(results)} rows.")

        # Close the connection
        conn.close()
        logging.info(f"Connection to the database '{db_name}' closed.")

        return results

    except sqlite3.Error as e:
        logging.error(f"SQL Execution Error: {e}")
        raise Exception(f"SQL Execution Error: {e}")