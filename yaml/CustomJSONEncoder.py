import json
from robocorp import log
from ipaddress import IPv4Address

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
        cleaned_data = []
        for item in data:
            if 'command_output' in item and isinstance(item['command_output'], str):
                # Remove triple quotes and carriage returns
                item['command_output'] = item['command_output'].strip().replace("'''", "").replace('\r', '')
            cleaned_data.append(item)
        return cleaned_data
    return []  # Ensure that the function always returns a list