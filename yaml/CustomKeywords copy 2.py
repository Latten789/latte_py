from genie.utils.dq import Dq
from robot.api.deco import keyword
from robot.api import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from genie.testbed import load
#from deepdiff import DeepDiff
import re
import os
import json
import yaml
from robocorp import log
import logging


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




class CustomKeywords:
    @log.suppress
    #@keyword("Show commands")
    def show_commands(self, commands_file_path):
        # コマンドを格納するためのリストを初期化
        commands_list = []

        # テキストファイルを開いて各行をリストに読み込む
        with open(commands_file_path, 'r') as file:
            for line in file:
                # 各行の末尾の改行文字を削除してリストに追加
                commands_list.append(line.strip())
                
        return commands_list

    _instance = None
    _testbed_loaded = False

    @log.suppress
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CustomKeywords, cls).__new__(cls)
            cls._instance.testbed = None
            cls._instance.devices = []
        return cls._instance

    @log.suppress
    #@keyword("Init Testbed")
    def init_testbed(self, testbed_path, devices=None):
        if not self._testbed_loaded:
            self.testbed = load(testbed_path)
            
            # 指定されたデバイス名のみを含むデバイスリストを作成
            if devices:
                # devicesパラメータが指定されている場合、そのリストに含まれるデバイスのみをロード
                self.devices = [device for device in self.testbed.devices.values() if device.name in devices]
                logger.warn("デバイス制限中 ")

            else:
                # devicesパラメータが指定されていない場合、すべてのデバイスをロード
                self.devices = list(self.testbed.devices.values())
            
            self._testbed_loaded = True
            
            # ロードされたデバイスの名前をログに出力
            for device in self.devices:
                logger.info(f"Loaded device: {device.name}")

    @log.suppress
    #@keyword("Connect To All Devices")
    def connect_to_all_devices(self):
        for device in self.devices:
            device.connect()
            logger.info(f"Connected to device: {device.name}")
            

            
    #@keyword("Execute Command Parallel")
    def execute_command_parallel(self, command, devices=None):
        if not self.devices:
            raise ValueError("Device list is empty. Ensure that the testbed is correctly loaded and devices are accessible.")

        if devices:
            # デバイス名のリストに基づいて、対象デバイスをフィルタリング
            target_devices = [device for device in self.devices if device.name in devices]
        else:
            # 引数が与えられない場合、すべてのデバイスが対象
            target_devices = self.devices

 
        @log.suppress
        def execute_command(device):
            output = device.execute(command)
            device_info = {
                'name': device.name,
            #    'os': device.os,
            #    'ip': device.connections.cli.ip,  # デバイスの接続情報に応じて変更する場合があります
                'command_output': output
            }
            return device_info
        
        results = []
        command_outputs = []
        with ThreadPoolExecutor(max_workers=len(target_devices)) as executor:
            futures = [executor.submit(execute_command, device) for device in target_devices]
            for future in as_completed(futures):
                result = future.result()
                #results.append(result)
                command_output_html = result["command_output"].replace("\n", "<br>")             # `command_output`をHTML形式で表示
                log.html(f"<pre>Device: {result['name']}<br>Output:<br>{command_output_html}</pre>")
            # for future in as_completed(futures):
            #     results.append(future.result())

            #     # command_outputs = [
            #     #     result["command_output"].replace("\n", "<br>") 
            #     #     for result in results
            #     # ]
            #     command_outputs.append(future.result()["command_output"].replace("\n", "<br>"))                # `command_output`をHTML形式で表示
            #     cleaned_results_html = "<br><br>".join(command_outputs)  # 各出力の間に空白行を追加

            #     # HTMLにラップしてログ出力
            #     log.html(f"<pre>Command Output:<br>{cleaned_results_html}</pre>")  

                
        @log.suppress
        def natural_sort_key(item):
                # 先頭の文字列に続く最初の数字セットを抽出
                match = re.search(r"\d+", item['name'])
                if match:
                    # 数字部分が見つかった場合は、その数値を基準にする
                    return int(match.group())
                else:
                    # 数字部分がない場合は、辞書順で最後にくるようにする
                    return float('inf')

        # Perform the sort (in-place)
        results.sort(key=natural_sort_key)


        return results
    
    @log.suppress
    #@keyword("Disconnect From All Devices")
    def disconnect_from_all_devices(self):
        for device in self.devices:
            device.disconnect()
            logger.info(f"Disconnected from device: {device.name}")
            

# unicon_logger = logging.getLogger('unicon')
# for handler in unicon_logger.handlers:
#     if isinstance(handler, logging.StreamHandler):  # 標準出力ハンドラを特定
#         unicon_logger.removeHandler(handler)  # 削除

