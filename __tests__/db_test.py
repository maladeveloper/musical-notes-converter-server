"""Houses the tests for the database access functions"""
import unittest
from src.db import (
    connect,
    close,
    add_job,
    add_instrument,
    delete_job,
    get_instruments,
    get_num_total_instruments,
    job_status,
    get_job_id,
    get_job_by_id
)


class BaseDBTester(unittest.TestCase):
    def setUp(self):
        self.conn = connect()
        self.cur = self.conn.cursor()

    def tearDown(self):
        close(self.conn)


class TestAddJob(BaseDBTester):
    def test_addition_of_job(self):
        num_instruments = 12344
        title = "hi"
        main_sheet = "bye"

        job_id = add_job(self.conn, title, main_sheet, num_instruments)

        self.cur.execute("""SELECT * FROM job WHERE id=%s""", (job_id,))
        records = self.cur.fetchall()
        self.assertEqual(records, [(job_id, num_instruments, title, main_sheet)])

        # Clean up
        self.cur.execute("""DELETE FROM job WHERE id=%s""", (job_id,))
        self.conn.commit()


class TestAddInstrument(BaseDBTester):
    def test_addition_of_instrument(self):
        name = "hellomotto"
        job_id = add_job(self.conn, "title", "main_sheet", 99)

        add_instrument(self.conn, job_id, name)

        self.cur.execute(
            """SELECT * FROM instrument WHERE job=%s""", (job_id,))
        records = self.cur.fetchall()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], name)
        self.assertEqual(records[0][2], job_id)

        # Clean up
        # Note: Deleting Job automatically deletes the instruments associated
        # with it
        self.cur.execute("""DELETE FROM job WHERE id=%s""", (job_id,))
        self.conn.commit()


class TestDeleteJob(BaseDBTester):
    def test_deletion_of_job(self):
        job_id = add_job(self.conn, "title", "main_sheet", 99)
        add_instrument(self.conn, job_id, "yoo")

        delete_job(self.conn, job_id)

        self.cur.execute("""SELECT * FROM job WHERE id=%s""", (job_id,))
        jobs = self.cur.fetchall()
        self.assertEqual(jobs, [])
        self.cur.execute("""SELECT * FROM instrument WHERE job=%s""", (job_id,))
        instruments = self.cur.fetchall()
        self.assertEqual(instruments, [])


class TestGetInstruments(BaseDBTester):
    def test_get_instruments_for_job(self):
        job_id = add_job(self.conn, "title", "main_sheet", 99)
        add_instrument(self.conn, job_id, "yoo")
        add_instrument(self.conn, job_id, "anotherone")
        add_instrument(self.conn, job_id, "yepp")

        instruments = get_instruments(self.conn, job_id)
        self.assertEqual(instruments, ['yoo', 'anotherone', 'yepp'])

        # Clean up
        delete_job(self.conn, job_id)


class TestGetTotalNumInstruments(BaseDBTester):
    def test_get_total_number_of_instruments_job_has(self):
        num_instruments = 82
        job_id = add_job(self.conn, "title", "main_sheet", num_instruments)

        num = get_num_total_instruments(self.conn, job_id)

        self.assertEqual(num, num_instruments)

        # Clean up
        delete_job(self.conn, job_id)


class TestJobStatus(BaseDBTester):
    def test_get_job_status(self):
        num_instruments = 82
        job_id = add_job(self.conn, "title", "main_sheet", num_instruments)
        add_instrument(self.conn, job_id, "yoo")
        add_instrument(self.conn, job_id, "anotherone")
        add_instrument(self.conn, job_id, "yepp")

        status = job_status(job_id)

        self.assertEqual(status, {"message": "Running", "doneInstrumentsArr": ['yoo', 'anotherone', 'yepp']})

        # Clean up
        delete_job(self.conn, job_id)

    def test_done_job_status(self):
        job_id = 1234
        status = job_status(job_id)

        self.assertEqual(status, {"message": "Done"})


class TestGetJobId(BaseDBTester):
    def test_get_job_when_present(self):
        num_instruments = 12344
        title = "hi"
        main_sheet = "bye"
        expected_job_id = add_job(self.conn, title, main_sheet, num_instruments)

        job_id = get_job_id(self.conn, title, main_sheet, num_instruments)

        self.assertEqual(expected_job_id, job_id)

        # Clean up
        delete_job(self.conn, job_id)

    def test_get_job_when_not_present(self):
        num_instruments = 12344
        title = "hi"
        main_sheet = "bye"

        job_id = get_job_id(self.conn, title, main_sheet, num_instruments)

        self.assertEqual(None, job_id)


class TestGetJobById(BaseDBTester):
    def test_get_job_by_id(self):
        num_instruments = 12344
        title = "hi"
        main_sheet = "bye"
        job_id = add_job(self.conn, title, main_sheet, num_instruments)

        recieved_title, recieved_main_sheet, recieved_num_instruments = get_job_by_id(self.conn, job_id)
        self.assertEqual([recieved_title, recieved_main_sheet, recieved_num_instruments],
                         [title, main_sheet, num_instruments])

        # Clean up
        delete_job(self.conn, job_id)

    def test_get_job_when_not_present(self):
        job_id = 12344
        self.assertEqual(get_job_by_id(self.conn, job_id), None)


if __name__ == '__main__':
    unittest.main()
