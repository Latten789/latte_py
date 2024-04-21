from robocorp.tasks import task
from robocorp.log import console_message
from genie.utils.dq import Dq
from robot.api.deco import keyword
from robot.api import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from genie.testbed import load
from CustomKeywords import CustomKeywords

import os
import json
import yaml
from ipaddress import IPv4Address
from robocorp.log import setup_auto_logging
from robocorp import log
#setup_auto_logging()
#log.setup_log(log_level=log.FilterLogLevel.CRITICAL)

class CustomJSONEncoder(json.JSONEncoder):
    @log.suppress
    def default(self, obj):
        if isinstance(obj, IPv4Address):
            return str(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
    
@log.suppress
def clean_command_output(data):
    if isinstance(data, list):
        for item in data:
            if 'command_output' in item:
                item['command_output'] = item['command_output'].replace('\r', '')
    return data


@task("Start")
@log.suppress
def start():
    CustomKeywords().init_testbed("testbed.yaml")
    CustomKeywords().connect_to_all_devices()
    

@task
def gather_log():
    
    for command in CustomKeywords().show_commands("./yaml/show"):
     results = CustomKeywords().execute_command_parallel(command)
     cleaned_results = clean_command_output(results)
     for result in cleaned_results:
        result_str = json.dumps(result, cls=CustomJSONEncoder).replace("\n", " ").replace("\\", "")
        logger.info(result_str)
