import logging
import os
import sys

from configs_validator import ConfigsValidator
from dotenv import load_dotenv
from pydantic import ValidationError


_logger = logging.getLogger(__name__)

load_dotenv('configs/.env')

is_prod = os.environ.get('IS_PROD') in [1, True, 'true', 'True']

try:
    config_parameters = ConfigsValidator(**os.environ)
except ValidationError as e:
    _logger.critical(exc_info=e, msg='Env parameters validation')
    sys.exit(-1)

config_parameters.IS_PROD = is_prod
