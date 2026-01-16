"""
Database Query Utility for RAJU-GPT Project

This file contains utility functions for querying the SQLite database.
You can add custom database queries and operations here.

Usage:
    python db_qurery.py
"""
import sqlite3
from pathlib import Path

# Get the database path
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'db.sqlite3'


def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)


def get_all_users():
    """Get all registered users"""
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("SELECT id, username, email, first_name, last_name, date_joined FROM auth_user")
    results = cursor.fetchall()
    con.close()
    return results


def get_chat_history(user_id=None):
    """Get chat history for a specific user or all users"""
    con = get_connection()
    cursor = con.cursor()
    
    if user_id:
        cursor.execute("""
            SELECT u.username, c.user_message, c.bot_response, c.timestamp 
            FROM gpt_app_chat_data c
            JOIN auth_user u ON c.user_id = u.id
            WHERE c.user_id = ?
            ORDER BY c.timestamp DESC
            LIMIT 50
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT u.username, c.user_message, c.bot_response, c.timestamp 
            FROM gpt_app_chat_data c
            JOIN auth_user u ON c.user_id = u.id
            ORDER BY c.timestamp DESC
            LIMIT 50
        """)
    
    results = cursor.fetchall()
    con.close()
    return results


def get_user_stats():
    """Get statistics about users and their chat activity"""
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("""
        SELECT 
            u.username,
            u.email,
            COUNT(c.id) as chat_count,
            MAX(c.timestamp) as last_chat
        FROM auth_user u
        LEFT JOIN gpt_app_chat_data c ON u.id = c.user_id
        GROUP BY u.id
    """)
    results = cursor.fetchall()
    con.close()
    return results


if __name__ == "__main__":
    # Example usage
    print("=== RAJU-GPT Database Utility ===\n")
    
    print("1. All Users:")
    users = get_all_users()
    for user in users:
        print(f"   ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
    
    print("\n2. User Statistics:")
    stats = get_user_stats()
    for stat in stats:
        print(f"   User: {stat[0]}, Chats: {stat[2]}, Last Active: {stat[3]}")
    
    print("\n3. Recent Chat History:")
    chats = get_chat_history()
    for chat in chats[:5]:  # Show only 5 recent chats
        print(f"   {chat[0]}: {chat[1][:50]}...")  # First 50 chars of message
# cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (id integer primary key, name VARCHAR(200), mobile_no VARCHAR(255), email VARCHAR(255) NULL)''')


# Specify the column indices you want to import (0-based index)
# Example: Importing the 1st and 3rd columns
# desired_columns_indices = [0, 20]

# # Read data from CSV and insert into SQLite table for the desired columns
# with open('contacts.csv', 'r', encoding='utf-8') as csvfile:
#     csvreader = csv.reader(csvfile)
#     for row in csvreader:
#         selected_data = [row[i] for i in desired_columns_indices]
#         cursor.execute(''' INSERT INTO contacts (id, 'name', 'mobile_no') VALUES (null, ?, ?);''', tuple(selected_data))

# # Commit changes and close connection
# con.commit()
# con.close()

# query = "INSERT INTO contacts VALUES (null,'randhir', '6201849307', 'null')"
# cursor.execute(query)
# con.commit()

# query = 'Raju'
# query = query.strip().lower()

# cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
# results = cursor.fetchall()
# print(results[0][0])