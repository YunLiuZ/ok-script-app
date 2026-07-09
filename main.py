import ok
from src.config import config

import logging

if __name__ == '__main__':
    class Id_f(logging.Filter):
        def filter(self, record):
            return "player id check failed" not in record.getMessage()
    logging.getLogger("ok").addFilter(Id_f())
    config = config
    ok = ok.OK(config)
    ok.start()
