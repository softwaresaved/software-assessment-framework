import logging

class Software:
    # TODO - Instantiate from JSON string
    def __init__(self, software_id, name, description, version, submitter, submitted, url, upload_path):
        logging.debug("Creating new instance of Software: "+name)
        self.software_id = software_id
        self.name = name
        self.description = description
        self.version = version
        self.submitter = submitter
        self.submitted = submitted
        self.url = url
        self.upload_path = upload_path
