from loguru import logger
from pathlib import Path
import os

def initalize_logger():
     MainPath = Path(os.path.realpath(__file__)).parent.parent
     logger.add('{}\\log.log'.format(MainPath), rotation='1 MB')
     


def not_number(x):
        '''
        check if x isn't a number
        '''
        try: 
            float(x)
            return False
        except ValueError:
            return True