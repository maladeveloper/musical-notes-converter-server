import os
import psycopg2
from random import randrange

def connect():
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def close(conn):
    conn.close()

def add_job(conn, num_instruments):
    job_id = randrange(1000000,10000000) 
    conn.cursor().execute("""INSERT INTO job (id, num_instruments) VALUES (%s, %s);""", (job_id, num_instruments))
    conn.commit()
    return job_id

def add_instrument(conn, job_id, name):
    conn.cursor().execute("""INSERT INTO instrument (name, job) VALUES (%s, %s);""", (name, job_id))
    conn.commit()

def get_instruments(conn, job_id):
    cur = conn.cursor() 
    cur.execute("""SELECT name FROM instrument WHERE job=%s""", (job_id,))
    return [ inst[0] for inst in cur.fetchall()]

def get_num_total_instruments(conn, job_id):
    cur = conn.cursor() 
    cur.execute("""SELECT num_instruments FROM job WHERE id=%s""", (job_id,))
    return cur.fetchall()[0][0]

def delete_job(conn, job_id):
    conn.cursor().execute("""DELETE FROM job WHERE id=%s""", (job_id,))
    conn.commit()

def job_status(job_id):
    conn = connect()
    return {
            "totalInstrumentsNum":get_num_total_instruments(conn, job_id),
            "doneInstrumentsArr": get_instruments(conn, job_id)
            }



