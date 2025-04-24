import boto3
from botocore.exceptions import ClientError
import sqlite3
import json
from sample_data import SAMPLE_DATA  # Import the sample data

# this is a runtime parameter of AWS Bedrock

session = boto3.Session(profile_name='pkawsazurelogin')
bedrock_runtime = session.client('bedrock-runtime', region_name='us-east-1')
bedrock_modedl_id = 'cohere.command-text-v14'  # replace with your model id
#bedrock_modedl_id = 'anthropic.claude-3-5-sonnet-20240620-v1:0'

# payload =  "Generate a SQL query to select records from sample_table where the  city is  New York.","max_tokens";
# payload =  "Generate a SQL query to select distinct names from sample_table where the name starts with p or q or r or s."
# payload =  "Generate a SQL query to select records from sample_table whose name has X in it.","max_tokens"
               
# payload = "Generate a SQL query to select records from sample_table where the city has India in the city name."

payload = "Generate a SQL query to get the sum of all the ages where the person is from cities that are either Los Angeles or San Francisco."
                

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
        "5. Use this SQL Statements to generate SQL queries or provide insights as requested.\n\n"
    )
    
    # Return the prompt with the DDL schema inserted
    return {"prompt": prompt_template.format(ddl_schema=ddl_schema, additional_text=additional_text), "max_tokens": 1000,
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

def setup_sample_db(db_name="sample.db"):
    """
    Sets up a sample SQLite3 database with a sample table and data.
    """
    # Connect to the SQLite3 database (creates the file if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create a sample table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sample_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            city TEXT NOT NULL
        )
    ''')

    # Insert sample data
    cursor.executemany('''
        INSERT INTO sample_table (name, age, city)
        VALUES (?, ?, ?)
    ''', SAMPLE_DATA)

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print(f"Sample database '{db_name}' has been set up successfully.")


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

# Function to extract the entire DDL from the database
def extract_ddl_from_db(db_name):
    """
    Extracts the entire DDL (Data Definition Language) from the specified SQLite3 database.
    """
    # Connect to the SQLite3 database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Get the list of tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    ddl_statements = []

    for table in tables:
        table_name = table[0]

        # Get the CREATE TABLE statement for each table
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}';")
        create_statement = cursor.fetchone()[0]
        ddl_statements.append(create_statement)

    # Close the connection
    conn.close()

    return ddl_statements

# Feed the DDL to the Bedrock model
def feed_ddl_to_bedrock_model(ddl_statements):
    """
    Feeds the DDL statements to the Bedrock model for processing.
    """
    # Convert the DDL statements to a single string
    ddl_string = "\n".join(ddl_statements)

    # Invoke the Bedrock model with the DDL string
    response = invoke_bedrock_model(bedrock_modedl_id, prompt_template(ddl_string, payload))

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

if __name__ == "__main__":
    # Set up the sample database
    setup_sample_db()

    
    response = feed_ddl_to_bedrock_model(extract_ddl_from_db("sample.db"))
    print("Bedrock Model Response:", response)

    #extract the sql query from the response
    sql_query = response.split("```sql")[1].split("```")[0].strip()
   
    print("Generated SQL Query:", sql_query)
    results = run_sql_query("sample.db", sql_query)
    print("Results from Generated SQL Query:", results)  
    for row in results:
        print("Retrived row: ", row)
