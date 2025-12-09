import logging
from logging.config import dictConfig

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'level': 'INFO',
            'filename': 'logs/app.log',
        },
        'debug-file-log': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'level': 'DEBUG',
            'filename': 'logs/debug.log',
        },
        'error-file-log': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'level': 'ERROR',
            'filename': 'logs/error.log',
        },
    },
    'loggers': {
        'missingETL': {
            'handlers': ['console', 'file', 'error-file-log', 'debug-file-log'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file', 'error-file-log', 'debug-file-log'],
    }
}

def setup_logging():
    dictConfig(LOGGING_CONFIG)

def get_logger(logger_name='missingETL', module_name=None):
    if module_name:
        return logging.getLogger(logger_name).getChild(module_name)

    return logging.getLogger(logger_name)
