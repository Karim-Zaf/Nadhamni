import sqlite3
import datetime

DB_PATH = "nadhamni.db"

def get_connection () : 
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db () : 
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY autoincrement,
        start_time TEXT NOT NULL,
        end_time TEXT,
        final_score INTEGER
    )
""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cycles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        iteration INTEGER NOT NULL,
        app_name TEXT,
        category TEXT,
        presence TEXT, 
        score INTEGER,
        timestamp TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    )
""")
    conn.commit()
    conn.close()


def create_session() :
    conn = get_connection() 
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO sessions(start_time) VALUES ('{datetime.datetime.now().isoformat()}')")
    session_id = cursor.lastrowid
    conn.commit() 
    conn.close()
    return session_id

def save_cycle (session_id, iteration, app_name, category, presence, score) :
    conn = get_connection() 
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO cycles(session_id,iteration,app_name,category, presence,score, timestamp) 
                   VALUES (?,?,?,?,?,?,?)""", (session_id, iteration, app_name, category, presence, score,datetime.datetime.now().isoformat()))
    conn.commit() 
    conn.close()

def end_session (session_id,final_score):
    conn = get_connection() 
    cursor = conn.cursor()
    cursor.execute("""UPDATE sessions set final_score = ? , end_time = ? WHERE id = ? """, (final_score,datetime.datetime.now().isoformat(),session_id))
    conn.commit() 
    conn.close()
