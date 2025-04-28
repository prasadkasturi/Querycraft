from utils.database_utils import is_database_empty, load_sql_data, extract_ddl_from_db
from utils.bedrock_utils import BedrockInvoker
import sqlite3
import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
# Resolve the absolute path of the SQL file
sql_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_file", "SampleData.sql"))  # Correct path

# Initialize BedrockInvoker
bedrock_invoker = BedrockInvoker(profile_name='pkawsazurelogin', region_name='us-east-1')

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
        "As a highly intelligent SQL expert, analyze the following DDL schema to understand the structure, "
        "relationships, and constraints of the database. Based on this schema, generate standard SQL syntax queries supported by SQLite3.\n"
        "or provide insights as requested.\n\n"
        "Instructions:\n"
        "1. Identify and remember the exact tables, columns, data types, and constraints (e.g., PRIMARY KEY, FOREIGN KEY) based on the schema {ddl_schema}.\n"
        "2. Understand relationships between tables (if any).\n"
        "3. query: {additional_text}\n\n"
        "4. Use the query to generate simple yet highly optimized SQL query.\n\n"
        "5. Verify that generated SQL query only has the columns that are part of the provided schema'.\n\n"
        "6. Give the response output as only the requested SQL Query\n"
    )
    return {"prompt": prompt_template.format(ddl_schema=ddl_schema, additional_text=additional_text),
            "temperature": 0.1,
            "stop_sequences": []}

def process_sql_request(prompt, db_name):
    """
    Processes the SQL request: checks database, invokes Bedrock, and runs the SQL query.
    """
    
    
    max_retries = 2  # Number of retries for Bedrock invocation

    
    ddl_statements = extract_ddl_from_db(db_name)
    logging.info("Extracted DDL statements from the database.", ddl_statements)

    # Retry mechanism for Bedrock invocation
    response = None
    prompt_text = prompt_template(ddl_statements, prompt)["prompt"]
    for attempt in range(max_retries + 1):
        try:
            logging.info("Attempting to invoke Bedrock model (Attempt %d/%d)... Prompt: %s", attempt + 1, max_retries + 1, prompt_text)
            # Generate SQL query using Bedrock
            response = bedrock_invoker.invoke_model(
                model_id="cohere.command-text-v14",  # Replace with your model ID
                prompt=prompt_text,
                max_tokens=512,
                temperature=0.1,
                stop_sequences=[]
            )
            if response:  # Exit the retry loop if a valid response is received
                logging.info("Bedrock model invocation successful.", response)
                break
        except Exception as e:
            if attempt < max_retries:
                logging.warning(f"Retrying Bedrock invocation (Attempt {attempt + 1}/{max_retries})...")
            else:
                logging.error(f"Bedrock Invocation Failed: {e}")
                raise Exception(f"Bedrock Invocation Failed: {e}")

    # Check if the response is None
    if response is None:
        logging.error("Bedrock returned no response.")
        raise Exception("Bedrock returned no response.")

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