import os
import pyodbc
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_env_vars():
    # Initialize dictionary with default values set to None
    env_vars = {
        'server': os.getenv('MATRIKA_DB_SERVER', None),
        'database': os.getenv('MATRIKA_DB_NAME', None),
        'username': os.getenv('MATRIKA_DB_USERNAME', None),
        'password': os.getenv('MATRIKA_DB_PASSWORD', None)
    }
    
    # Ask for any missing values
    if env_vars['server'] is None:
        env_vars['server'] = input('Server: ')
    if env_vars['database'] is None:
        env_vars['database'] = input('Database: ')
    if env_vars['username'] is None:
        env_vars['username'] = input('Username: ')
    if env_vars['password'] is None:
        env_vars['password'] = input('Heslo: ')

    return env_vars

def connect_to_db():


    env_vars = get_env_vars()
    server = env_vars['server']
    database = env_vars['database']
    username = env_vars['username'] 
    password = env_vars['password']


    # Create connection string for MSSQL 2019
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
        f"PWD={password}"
        
    )

    # Establish connection
    conn = pyodbc.connect(conn_str)
    print("Successfully connected to the database!")
    return conn
        
        
