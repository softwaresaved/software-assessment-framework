import logging
import config
from app import app


# Run this to start the webapp

def main():
    # Set up logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s %(funcName)s() - %(message)s',
                        filename=config.log_file_name,
                        level=config.log_level)
    logging.info('-- Starting the Software Assessment Framework --')
    app.run(debug=True)

if __name__ == '__main__':
    main()