# coding: utf-8
import logging.config


def do_logger():
    logging.config.fileConfig('logging.conf')
    _logger = logging.getLogger('server')
    _logger.info('aaaaaa')
    _logger.debug('bbbb')


if __name__ == '__main__':
    do_logger()