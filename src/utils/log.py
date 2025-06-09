import logging #.config
import colorlog
 
def add_logger_handler(self):
    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        '%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'blue',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )

    handler.setFormatter(formatter)
    self.logger.addHandler(handler)
    
def logger(msg):
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(f'{datetime.datetime.now().strftime( "%H:%M" )}')
        logger.info(str(msg))

    
