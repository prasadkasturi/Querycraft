import boto3
from botocore.exceptions import ClientError
import sqlite3
import json
from sample_data import SAMPLE_DATA  # Import the sample data
import os
from bedrock_invoke import BedrockInvoker
from database_utils import is_database_empty, load_sql_data, extract_ddl_from_db

# this is a runtime parameter of AWS Bedrock

session = boto3.Session(profile_name='pkawsazurelogin')
bedrock_runtime = session.client('bedrock-runtime', region_name='us-east-1')
bedrock_modedl_id = 'cohere.command-text-v14'  # replace with your model id
#bedrock_modedl_id = 'anthropic.claude-3-5-sonnet-20240620-v1:0'

# payload =  "Generate a SQL query to select records from sample_table where the  city is  New York.","max_tokens";
# payload =  "Generate a SQL query to select distinct names from sample_table where the name starts with p or q or r or s."
# payload =  "Generate a SQL query to select records from sample_table whose name has X in it.","max_tokens"
               
# payload = "Generate a SQL query to select records from sample_table where the city has India in the city name."

#payload = "Generate a SQL query to get the sum of all the ages where the person is from cities that are either Los Angeles or San Francisco."
payload = "Generate a SQL query to select records from sample_db where which authors books are most loaned along with the titles."
# payload = "Generate a SQL query to select records from sample_db where which authors books are least loaned along with the titles in the recent times."


def prompt_template(ddl_schema, additional_text):
    """
    Generates a prompt for the LLM to understand the DDL schema and generate SQL queries.
    """
    prompt_template = (
        "As a highly intelligent SQL expert, analyze the following DDL schema to understand the structure, "
        "relationships, and constraints of the database. Based on this schema, generate standard SQL syntax queries supported by SQLite3.\n"
        "or provide insights as requested.\n\n"
        "Instructions:\n"
        "1. If the schema {ddl_schema} is already created, stop creating and proceed to the next step.\n"
        "2. Identify the tables, columns, data types, and constraints (e.g., PRIMARY KEY, FOREIGN KEY) based on the schema.\n"
        "3. Understand relationships between tables (if any).\n"
        "4. {additional_text}\n\n"
        "5. Use this SQL Statements to generate highly optimized SQL queries with best explain plans or provide insights as requested.\n\n"
    )
    
    # Return the prompt with the DDL schema inserted
    return {"prompt": prompt_template.format(ddl_schema=ddl_schema, additional_text=additional_text),
        "temperature": 0.1,
        "stop_sequences": []}


# function to invoke the Bedrock model
def invoke_bedrock_model(model_id, payload):   
    try: 
        response = bedrock_runtime.invoke_model(
           modelId=model_id,
            body=json.dumps({
                "prompt": payload["prompt"],
            }).encode('utf-8'),  # Use "prompt" as the key for the input text
            contentType="application/json"
            # accept="application/json"
        )
        return json.loads(response['body'].read().decode('utf-8'))['generations'][0]['text']
    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)


def run_sql_query(db_name, query):
    """
    Runs a SQL query on the specified SQLite3 database.
    """
    # Connect to the SQLite3 database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Execute the SQL query
    cursor.execute(query)

    # Fetch all results
    results = cursor.fetchall()

    # Close the connection
    conn.close()

    return results

# Initialize the BedrockInvoker
bedrock_invoker = BedrockInvoker(profile_name='pkawsazurelogin', region_name='us-east-1')

def feed_ddl_to_bedrock_model(ddl_statements, model_id):
    """
    Feeds the DDL statements to the specified Bedrock model for processing.
    """
    # Convert the DDL statements to a single string
    ddl_string = "\n".join(ddl_statements)

    # Invoke the Bedrock model with the DDL string
    response = bedrock_invoker.invoke_model(
        model_id=model_id,
        prompt=prompt_template(ddl_string, payload)["prompt"],
        max_tokens=512,
        temperature=0.1,
        stop_sequences=[]
    )

    return response 


def plain_text_to_sql():
    """
    Converts a plain text prompt into a SQL query using the Bedrock model.
    """
    # Invoke the Bedrock model with the prompt
    response = invoke_bedrock_model(bedrock_modedl_id, payload)
    
    # Extract the SQL query from the response
    sql_query = response.strip()
    
    return sql_query


def setup_and_validate_database(db_name="sample.db", sql_file_path="SampleData.sql"):
    """
    Sets up the SQLite database and loads SQL data if the database is empty.
    Prints whether the database is empty and loading data or skipping the load.
    """
    if is_database_empty(db_name):
        print("Database is empty. Loading data from SampleData.sql...")
        load_sql_data(db_name, sql_file_path)
    else:
        print("Database is already populated. Skipping data load.")


if __name__ == "__main__":
    # Call the consolidated method to set up the database
    setup_and_validate_database()

    # Extract the DDL from the database
    ddl_statements = extract_ddl_from_db("sample.db")

    # Call the Bedrock model (e.g., Cohere or Anthropic)
    model_id = 'cohere.command-text-v14'  # Replace with the desired model ID
    response = feed_ddl_to_bedrock_model(ddl_statements, model_id)
    print("Bedrock Model Response:", response)

    # Extract the SQL query from the response
    if response:
        if "```sql" in response:
            sql_query = response.split("```sql")[1].split("```")[0].strip()
        else:
            print("Warning: SQL query markers not found in the response. Using the entire response as the query.")
            sql_query = response.strip()

        print("Generated SQL Query:", sql_query)

        # Run the SQL query
        results = run_sql_query("sample.db", sql_query)
        for row in results:
            print("Retrieved row: ", row)
    else:
        print("Error: No response received from the Bedrock model.")
