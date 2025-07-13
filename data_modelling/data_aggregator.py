
import pandas as pd
import sqlite3
import os

DB_FILE = "data_modelling/database.db"
USERS_CSV = "data_modelling/users.csv"
INTERACTIONS_CSV = "data_modelling/activity.csv"

def load_data_to_db(DB_FILE=DB_FILE):
    """
    Reads user and interaction data from CSV files and loads them into a SQLite database.
    This function creates two tables: 'users' and 'interactions'.
    If the tables already exist, they will be replaced.
    """
    try:
        # Read CSV files into pandas DataFrames
        print(f"Reading data from {USERS_CSV} and {INTERACTIONS_CSV}...")
        users_df = pd.read_csv(USERS_CSV)
        interactions_df = pd.read_csv(INTERACTIONS_CSV)

        # Establish a connection to the SQLite database
        print(f"Connecting to database: {DB_FILE}...")
        conn = sqlite3.connect(DB_FILE)

        # Load the data into the database
        print("Writing data to 'users' and 'interactions' tables...")
        users_df.to_sql("users", conn, if_exists="replace", index=False)
        interactions_df.to_sql("interactions", conn, if_exists="replace", index=False)

        # Close the connection
        conn.close()
        print("Data loading complete. Database is ready.")

    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure the CSV files are in the correct directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def run_aggregation_query(DB_FILE=DB_FILE):
    """
    Connects to the SQLite database and runs the aggregation query.

    Returns:
        A pandas DataFrame containing the aggregated results.
    """
    sql_query = """
    SELECT
        DATE(i.timestamp) AS day,
        u.gender,
        u.city,
        COUNT(i.user_id) AS total_interactions,
        SUM(CASE WHEN i.like_type = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(i.user_id) AS percentage_of_likes,
        SUM(CASE WHEN i.like_type = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(i.user_id) AS percentage_of_dislikes
    FROM
        interactions i
    JOIN
        users u ON i.user_id = u.user_id
    GROUP BY
        day,
        u.gender,
        u.city
    ORDER BY
        day,
        u.gender,
        u.city;
    """
    try:
        print("Connecting to database and running aggregation query...")
        conn = sqlite3.connect(DB_FILE)
        
        # Execute the query and load results into a DataFrame
        aggregated_df = pd.read_sql_query(sql_query, conn)
        
        conn.close()
        print("Query complete.")
        return aggregated_df
    except sqlite3.OperationalError as e:
        print(f"Error executing query: {e}")
        print("Please ensure the database and tables exist by running the script without arguments first.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    # Step 1: Load the data from CSVs into the database
    # load_data_to_db()
    
    # Step 2: Run the aggregation query and get the results
    results_df = run_aggregation_query()

    # Step 3: Display the results
    if results_df is not None:
        print("\n--- Aggregated Interaction Metrics ---")
        print(results_df.to_string())

