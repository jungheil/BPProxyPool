import multiprocessing
import sys

from config import db_config
from db.dbClient import DbClient
from handler.logger import LogHandler

logger = LogHandler("launcher")


def start_server():
    _before_start()
    from server.server import runFlask

    runFlask()


def start_scheduler():
    _before_start()
    from helper.scheduler import runScheduler

    runScheduler()


def _before_start():
    if _check_db():
        logger.error(
            "Database connection failed, please check the database configuration"
        )
        sys.exit(1)


def start_all():
    scheduler_process = multiprocessing.Process(target=start_scheduler)
    server_process = multiprocessing.Process(target=start_server)
    scheduler_process.start()
    server_process.start()
    scheduler_process.join()
    server_process.join()


def _check_db():
    db = DbClient(db_config["db_conn"])
    return db.test()
