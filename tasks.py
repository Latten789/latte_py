from robocorp.tasks import task
from robocorp.log import console_message
from genie.utils.dq import Dq
from robot.api.deco import keyword
from robot.api import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from genie.testbed import load
from CustomKeywords import CustomKeywords
from CustomJSONEncoder import CustomJSONEncoder
from CustomJSONEncoder import clean_command_output
import os
import json
import yaml
from ipaddress import IPv4Address
from robocorp.log import setup_auto_logging
from robocorp import log
import html
import logging
#setup_auto_logging()
#log.setup_log(log_level=log.FilterLogLevel.CRITICAL)


# Uniconのロギングを抑制するための設定
logging.basicConfig(level=logging.WARNING)  # WARNINGレベル以上のみログに表示

# Uniconのログを抑制
unicon_logger = logging.getLogger('unicon')
unicon_logger.setLevel(logging.WARNING)  # INFO以下のログを抑制

# ルートロガーの設定
root_logger = logging.getLogger()  # すべてのロギングのルート
root_logger.setLevel(logging.WARNING)  # INFO以下のログを抑制

# 既存の全ハンドラーのログレベルを変更
for handler in root_logger.handlers:
    handler.setLevel(logging.WARNING)  # 全ハンドラーのレベルをWARNINGに


@task
#@log.suppress
def n_log_start():
    CustomKeywords().init_testbed("testbed.yaml")
    #CustomKeywords().init_testbed("testbed.back.yaml")
    CustomKeywords().connect_to_all_devices()
    
@task
#@log.suppress(variables=False)
def gather_log():
    #log.html("Command Results")  # セクションタイトル    
    #for command in CustomKeywords().show_commands("./yaml/show"):
    for command in CustomKeywords().show_commands("./yaml/show2"):
        results = CustomKeywords().execute_command_parallel(command)
       # log.html(f"Executing Command: {command}")
        #log.info(f"{command}")

        for result in results:
        #  Convert the cleaned result to a JSON string, replace newlines and backslashes
            #cleaned_results_html = result["command_output"]
            #name_output    = result["name"]
            command_output = result["command_output"].replace("\n", "<br>")             # `command_output`をHTML形式で表示
            #cleaned_results_html = "<br><br>".join(command_outputs)  # 各出力の間に空白行を追加
            #log.html(f"<pre>{command_outputs}</pre>")
            # log.html(f"<pre>Device:{name_output}<br>Output:<br>{command_output}</pre>")
            log.html(f"<pre>{command_output}</pre>")
            
        # results = CustomKeywords().execute_command_parallel(command)
        # cleaned_results = clean_command_output(results)
        # `command_output`のみ抽出し、HTMLで改行を保持
        # command_outputs = [
        #     result["command_output"].replace("\n", "<br>") 
        #     for result in results
        # ]

        # # `command_output`をHTML形式で表示
        # cleaned_results_html = "<br><br>".join(command_outputs)  # 各出力の間に空白行を追加

        # # HTMLにラップしてログ出力
        # log.html(f"<pre>Command Output:<br>{cleaned_results_html}</pre>")        # # Convert each dictionary result to a JSON string and then to HTML format
        # cleaned_results_html = "<br>".join([json.dumps(result, cls=CustomJSONEncoder, indent=4, ensure_ascii=False).replace("\n", "<br>").replace(" ", "&nbsp;") for result in results])
        # # Use the log.html function to log HTML content
        # log.html(f"<pre>Cleaned Results:\n{cleaned_results_html}</pre>")
        # # log.html(f"Cleaned Results:<br>{cleaned_results_html}")        
        # # # リストの各辞書要素をJSON文字列に変換し、<br>タグで連結
        # # cleaned_results_html = "<br>".join([json.dumps(result, cls=CustomJSONEncoder, indent=4, ensure_ascii=False) for result in cleaned_results])
        # # # HTMLとしてログ出力
        # # log.info(f"Cleaned Results:<br>{cleaned_results_html}")
        # # # for result in cleaned_results:
        # # #     # Convert the cleaned result to a JSON string, replace newlines and backslashes
        # # #     result_str = json.dumps(result, cls=CustomJSONEncoder,indent=4, ensure_ascii=False).replace("\n", " ").replace("\\", "")
        # # #     # Ensure triple quotes are removed from the final JSON string

