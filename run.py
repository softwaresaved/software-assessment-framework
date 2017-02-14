from datetime import datetime

import app.models
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s %(funcName)s() - %(message)s')


def main():
    logging.info('Start')

    # TODO instantiate from JSON - perhaps add functionality in Software __init__()
    sw = app.models.Software(software_id=None,
                  name='Climate Analysis',
                  description='Contrived code for Software Carpentry workshops',
                  version='1.0',
                  submitter='JSR',
                  submitted=datetime.utcnow(),
                  url='https://github.com/js-robinson/climate-analysis')

    # process_software(sw)

if __name__ == '__main__':
    main()
