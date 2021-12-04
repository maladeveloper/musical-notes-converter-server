"""Houses all the functions in order to access the database"""
import os
from random import randrange
import psycopg2

def connect():
    database_url = os.environ['DATABASE_URL']
    conn = psycopg2.connect(database_url, sslmode='require')
    return conn


def close(conn):
    conn.close()


def add_job(conn, title, main_sheet, num_instruments):
    job_id = randrange(1000000, 10000000)
    conn.cursor().execute(
        """INSERT INTO job (id, title, main_sheet, num_instruments) VALUES (%s, %s, %s, %s);""",
        (job_id,
         title,
         main_sheet,
         num_instruments))
    conn.commit()
    return job_id


def add_instrument(conn, job_id, name):
    conn.cursor().execute(
        """INSERT INTO instrument (name, job) VALUES (%s, %s);""", (name, job_id))
    conn.commit()


def get_job_id(conn, title, main_sheet, num_instruments):
    cur = conn.cursor()
    cur.execute(
        """SELECT id FROM job WHERE title=%s AND main_sheet=%s AND num_instruments=%s""",
        (title,
         main_sheet,
         num_instruments))
    ids = cur.fetchall()

    if len(ids) == 0:
        return None
    return ids[0][0]


def get_job_by_id(conn, job_id):
    cur = conn.cursor()
    cur.execute(
        """SELECT title, main_sheet, num_instruments FROM job WHERE id=%s""", (job_id,))

    jobs = cur.fetchall()

    if len(jobs) == 0:
        return None

    return list(jobs[0])


def get_instruments(conn, job_id):
    cur = conn.cursor()
    cur.execute("""SELECT name FROM instrument WHERE job=%s""", (job_id,))
    return [inst[0] for inst in cur.fetchall()]


def get_num_total_instruments(conn, job_id):
    cur = conn.cursor()
    cur.execute("""SELECT num_instruments FROM job WHERE id=%s""", (job_id,))
    return cur.fetchall()[0][0]


def delete_job(conn, job_id):
    conn.cursor().execute("""DELETE FROM job WHERE id=%s""", (job_id,))
    conn.commit()


def job_status(job_id):
    """Creates the Job Status for the specified job id"""
    conn = connect()
    if not get_job_by_id(conn, job_id):
        return {"message": "Done"}
    return {
        "message": "Running",
        "doneInstrumentsArr": get_instruments(conn, job_id)
    }
