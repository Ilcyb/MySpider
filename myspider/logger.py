import logging

o_logger = logging.getLogger('ordinary')
e_logger = logging.getLogger('error')

o_logger.setLevel(logging.INFO)
e_logger.setLevel(logging.WARN)

ordinary_handler = logging.StreamHandler()
ordinary_handler.setLevel(logging.INFO)
ordinary_formmat = logging.Formatter("%(asctime)s - %(message)s")
ordinary_handler.setFormatter(ordinary_formmat)
o_logger.addHandler(ordinary_handler)

err_handler = logging.StreamHandler()
err_handler.setLevel(logging.WARN)
err_formmat = logging.Formatter("Error: [%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
err_handler.setFormatter(err_formmat)
e_logger.addHandler(err_handler)

def log(message, level=logging.INFO):
    if level >= logging.WARN:
        if level == logging.WARN:
            e_logger.warn(message)
        elif level == logging.ERROR:
            e_logger.error(message)
        elif level == logging.CRITICAL:
            e_logger.critical(message)
    else:
        if level == logging.INFO:
            o_logger.info(message)
        if level == logging.DEBUG:
            o_logger.debug(message)
