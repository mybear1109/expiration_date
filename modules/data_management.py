import sqlite3
import os
import streamlit as st

DB_PATH = "data/expiration_data.db"

def create_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            product_name TEXT,
            expiration_date TEXT,
            limit_day TEXT,
            manufacturer TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_product(record):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO product_table (barcode, product_name, expiration_date, limit_day, manufacturer)
        VALUES (?, ?, ?, ?, ?)
    """, (record["barcode"], record["product_name"], record["expiration_date"], record["limit_day"], record["manufacturer"]))
    conn.commit()
    conn.close()
