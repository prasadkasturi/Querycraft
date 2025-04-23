# QueryCraft

This project integrates AWS Bedrock with SQLite to dynamically generate and execute SQL queries using natural language prompts.

## Features
- Setup and populate a sample SQLite database.
- Extract DDL schema from the database.
- Generate SQL queries using AWS Bedrock.
- Execute generated SQL queries on the database.

## Requirements
- Python 3.x
- AWS CLI configured with Bedrock access
- SQLite

## Usage
1. Set up the database:
   ```bash
   python sql_gen.py