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

class CustomKeywords:
    def load_data_from_json_file(self, file_path):
        # JSONファイルからデータを読み込む
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    
    def load_data_from_dq_to_json_file(self, dq_data):
        # DqオブジェクトをJSONへ変換する
        if isinstance(dq_data, Dq):
            data = json.loads(json.dumps(dq_data.to_dict()))
        else:
            data = dq_data
        
        return data

    @keyword("Compare Route VRF Information")
    def compare_route_vrf_information(self, json_file_path, dq_data):
        dict_data_1 = self.load_data_from_json_file(json_file_path)
        dict_data_2 = dq_data  # dqデータをそのまま使用

        discrepancies = []

        for vrf, expected_vrf_data in dict_data_1['vrf'].items():
            if 'routes' in expected_vrf_data['address_family']['ipv4']:
                expected_routes = expected_vrf_data['address_family']['ipv4']['routes']
            else:
                expected_routes = {}

            actual_vrf_data = dict_data_2['vrf'].get(vrf, {}).get('address_family', {}).get('ipv4', {})
            actual_routes = actual_vrf_data.get('routes', {}) if actual_vrf_data else {}

            for route, expected_details in expected_routes.items():
                actual_details = actual_routes.get(route, {})

                expected_nexthops = self.get_nexthops(expected_details)
                actual_nexthops = self.get_nexthops(actual_details)

                if expected_nexthops != actual_nexthops:
                    discrepancies.append(f"Next hop mismatch for route {route} in VRF {vrf}: expected {expected_nexthops}, found {actual_nexthops}")
                else:
                    print(f"Route {route} in VRF {vrf}: expected next hops {expected_nexthops}, actual next hops {actual_nexthops}")

        if discrepancies:
            for discrepancy in discrepancies:
                print(discrepancy)
            raise AssertionError("Some route information did not match.")
        else:
            print("All route information matched successfully.")

    def get_nexthops(self, route_details):
        nexthops = set()

        # 'next_hop_list' キーが存在する場合、その中の 'next_hop' の値を抽出
        if 'next_hop_list' in route_details.get('next_hop', {}):
            for hop in route_details['next_hop']['next_hop_list'].values():
                nexthops.add(hop.get('next_hop'))

        # 'outgoing_interface' キーが存在する場合、そのキーを直接 nexthops に追加
        elif 'outgoing_interface' in route_details.get('next_hop', {}):
            for intf in route_details['next_hop']['outgoing_interface'].values():
                nexthops.add(intf.get('outgoing_interface'))

        return nexthops

    @keyword("Save Data To JSON File")
    def save_data_to_json_file(self, dq_or_dict, hostname, save_path):
        # データをJSON形式で保存
        if isinstance(dq_or_dict, Dq):
            dict_data = dq_or_dict.to_dict()
        else:
            dict_data = dq_or_dict
            
        # 保存先のディレクトリを確認し、存在しなければ作成
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # JSONファイルに保存
        file_path = os.path.join(save_path, f"{hostname}")

        with open(file_path, 'w') as file:
            json.dump(dict_data, file, indent=2)

    @keyword("Compare BGP VPNv4 Unicast Data")
    def compare_bgp_vpnv4_unicast_data(self, before_file_path, after_data_str):
        # 'before_data' をファイルから読み込む
        with open(before_file_path, 'r') as bf:
            before_data = json.load(bf)

        # 'after_data' が文字列の場合は JSON に変換
        after_data = json.loads(after_data_str) if isinstance(after_data_str, str) else after_data_str

        # 比較と結果の記録
        comparisons = self._compare_data(before_data, after_data)

        # 全ての比較結果を表示
        for comparison in comparisons:
            print(comparison['message'])

        # 不一致があった場合、エラーメッセージを表示
        if any(comp['is_diff'] for comp in comparisons):
            raise AssertionError("Some BGP VPNv4 Unicast data did not match.")

    def _compare_data(self, before_data, after_data):
        comparisons = []
        for rd, before_entries in before_data.items():
            after_entries = after_data.get(rd, [])

            for be in before_entries:
                matching_ae = next((ae for ae in after_entries if ae["Network"] == be["Network"] and ae["Best Path Info"] == be["Best Path Info"]), None)
                
                if matching_ae:
                    diffs = self._compare_entries(be, matching_ae)
                    if diffs:
                        comparisons.append({'is_diff': True, 'message': f'{rd} {be["Network"]} ({be["Best Path Info"].strip()}): ' + "; ".join(diffs)})
                    else:
                        comparisons.append({'is_diff': False, 'message': f'{rd} {be["Network"]} ({be["Best Path Info"].strip()}): No difference'})
                else:
                    comparisons.append({'is_diff': True, 'message': f'!!!!!!!!!{rd} {be["Network"]} ({be["Best Path Info"].strip()}): Entry missing in after data!!!!!!!!!'})

        return comparisons

    def _compare_entries(self, before_entry, after_entry):
        diffs = []
        if before_entry["Next Hop"] != after_entry.get("Next Hop"):
            diffs.append(f'!!!!!!!!!Next Hop changed from {before_entry["Next Hop"]} to {after_entry.get("Next Hop", "None")}!!!!!!!!!')

        # カラー値の比較
        if "Color" in before_entry or "Color" in after_entry:
            before_color = before_entry.get("Color", "Not present")
            after_color = after_entry.get("Color", "Not present")
            if before_color != after_color:
                diffs.append(f'!!!!!!!!!Color changed from {before_color} to {after_color}!!!!!!!!!')

        return diffs

    @keyword("Compare OSPF Neighbors Information")
    def compare_ospf_neighbors_information(self, json_file_path, dq_data):
        dict_data_1 = self.load_data_from_json_file(json_file_path)
        dict_data_2 = self.load_data_from_dq_to_json_file(dq_data)

        # VRFごとにOSPfネイバー情報を比較
        for vrf, expected_vrf_data in dict_data_1['vrfs'].items():
            actual_vrf_data = dict_data_2['vrfs'].get(vrf, {})
            expected_neighbors = expected_vrf_data.get('neighbors', {})
            actual_neighbors = actual_vrf_data.get('neighbors', {})

            for neighbor_ip, expected_neighbor_details in expected_neighbors.items():
                actual_neighbor_details = actual_neighbors.get(neighbor_ip, {})

                # Stateの確認
                expected_state = expected_neighbor_details.get('state', '')
                actual_state = actual_neighbor_details.get('state', '')
                assert expected_state == actual_state, f"State mismatch for neighbor {neighbor_ip} in VRF {vrf}"

                # Stateが FULL/ - であることを確認
                assert expected_state == "FULL/  -", f"Neighbor {neighbor_ip} in VRF {vrf} is not in the FULL state"

                print(f"Neighbor {neighbor_ip} in VRF {vrf} successfully compared and is in FULL state.")


    @keyword("Compare BGP Neighbors Session State")
    def compare_bgp_neighbors_session_state(self, json_file_path_1, dq_data):
        dict_data_1 = self.load_data_from_json_file(json_file_path_1)
        dict_data_2 = self.load_data_from_dq_to_json_file(dq_data)

        # BGPインスタンスの情報を取得
        for instance in dict_data_1['instance'].values():
            # VRFごとにネイバー情報を比較
            for vrf, expected_vrf_data in instance['vrf'].items():
                actual_vrf_data = dict_data_2.get('instance', {}).get('all', {}).get('vrf', {}).get(vrf, {})
                expected_neighbors = expected_vrf_data.get('neighbor', {})
                actual_neighbors = actual_vrf_data.get('neighbor', {})

                for neighbor_ip, expected_neighbor_details in expected_neighbors.items():
                    actual_neighbor_details = actual_neighbors.get(neighbor_ip, {})
                    
                    # セッションステートの比較
                    expected_session_state = expected_neighbor_details.get('session_state', '')
                    actual_session_state = actual_neighbor_details.get('session_state', '')
                    assert expected_session_state == actual_session_state, f"Session state mismatch for neighbor {neighbor_ip} in VRF {vrf}"

                    # セッションステートがestablishedであることを確認
                    #assert expected_session_state == "established", f"Neighbor {neighbor_ip} in VRF {vrf} session state is not established"

                    print(f"Neighbor {neighbor_ip} in VRF {vrf} session state expected.")
    
    @keyword("Load Ping Trace Data From Yaml")
    def load_ping_trace_data_from_yaml(self, yaml_file):
        with open(yaml_file, 'r') as file:
            ping_data = yaml.safe_load(file)
        print(ping_data)
        return ping_data

    @keyword("Generate Commands")
    def generate_commands(self, data, command_type):
        ping_commands = []
        for entry in data['tests']:
            VRF = entry['VRF']
            dest_addr = entry['dest_addr']
            source_addr = entry['source_addr']
            if command_type == 'ping':
                command = f'ping vrf {VRF} {dest_addr} source {source_addr}'
            elif command_type == 'traceroute':
                command = f'traceroute vrf {VRF} {dest_addr} source {source_addr}'
            else:
                raise ValueError("Invalid command type. Please use 'ping' or 'traceroute'.")
            ping_commands.append(command)
        return ping_commands

    @keyword("Load SR Ping Data From YAML")
    def load_sr_ping_data_from_yaml(self, yaml_file, device_name):
        with open(yaml_file, 'r') as file:
            self.ping_data = yaml.safe_load(file)

        if device_name not in self.ping_data:
            raise ValueError(f"Device {device_name} not found in YAML data")

        return self.ping_data[device_name]

    @keyword("Generate SR Commands")
    def generate_sr_commands(self, device_ping_data, command_type):
        commands = []
        for entry in device_ping_data:
            dest_addr = entry['dest_addr']
            source_addr = entry['source_addr']
            if command_type == 'sr-ping':
                command = f'ping sr-mpls {dest_addr} source {source_addr}'
            elif command_type == 'sr-traceroute':
                command = f'traceroute sr-mpls {dest_addr} source {source_addr}'
            else:
                raise ValueError(f"Unsupported command type: {command_type}")
            commands.append(command)
        return commands

    
    @keyword("Compare Ping Results")
    def compare_ping_results(self, before_data_file, after_data_list):
        # 'before_data' をファイルから読み込む
        with open(before_data_file, 'r') as file:
            before_data_list = json.load(file)

        before_commands = []  # before_data内のすべてのPINGコマンドを保持するリスト

        # before_dataのコマンドをリストに追加
        for before_data in before_data_list:
            before_ping = before_data.get("PING", {})
            before_commands.extend(before_ping.keys())

        for after_data in after_data_list:
            after_ping = after_data.get("PING", {})
            after_success_rate = None  # 変数をループの先頭で初期化

            for command, after_details in after_ping.items():
                after_success_rate = after_details.get("Success Rate")  # 成功率を取得

                if command in before_commands:
                    before_commands.remove(command)

                    # コマンドがbefore_dataにも存在する場合、Success Rateを比較
                    for before_data in before_data_list:
                        before_ping = before_data.get("PING", {})
                        if command in before_ping:
                            before_success_rate = before_ping[command].get("Success Rate")
                            if before_success_rate == after_success_rate:
                                print(f"'{command}' のSuccess Rateは一致しています: {before_success_rate}%")
                            else:
                                raise AssertionError(f"'{command}' のSuccess Rateが一致しません。Before: {before_success_rate}%, After: {after_success_rate}%")
                else:
                    # after_dataに存在し、before_dataに存在しないコマンドを検知
                    raise AssertionError(f"'{command}' コマンドはbefore_dataに存在しません。After: {after_success_rate}%")

        # before_commandsリストに残っているコマンドは、after_data_listに存在しなかったことを意味する
        if before_commands:
            missing_commands = ', '.join(before_commands)
            raise AssertionError(f"以下のコマンドがafter_data_listに存在しません: {missing_commands}")
        
    @keyword("Compare Traceroute Results")
    def compare_traceroute_results(self, before_file_path, after_parsed_data):
        with open(before_file_path, 'r') as file:
            before_data_list = json.load(file)

        # コマンドセットを取得
        before_commands = {list(item["Traceroute"].keys())[0] for item in before_data_list}
        after_commands = {list(item["Traceroute"].keys())[0] for item in after_parsed_data}

        # 存在しないコマンドを検証
        missing_in_before = before_commands - after_commands
        missing_in_after = after_commands - before_commands

        # 不一致があるかどうかを追跡するフラグ
        discrepancies_found = False

        # 存在しないコマンドのエラーは記録のみ行い、例外を投げない
        if missing_in_before:
            logger.info(f"以下のコマンドがafter_dataに存在しません: {missing_in_before}")
            discrepancies_found = True
        if missing_in_after:
            logger.info(f"以下のコマンドがbefore_dataに存在しません: {missing_in_after}")
            discrepancies_found = True

        # 全てのコマンドに対して検証を実行
        for after_item in after_parsed_data:
            traceroute_command = list(after_item["Traceroute"].keys())[0]
            after_hops = after_item["Traceroute"][traceroute_command]
            before_hops = next((item["Traceroute"][traceroute_command] for item in before_data_list if traceroute_command in item["Traceroute"]), {})

            for hop_num, after_hop_value in after_hops.items():
                before_hop_value = before_hops.get(hop_num)
                if before_hop_value != after_hop_value:
                    logger.info(f"コマンド {traceroute_command}, ホップ {hop_num}: 不合格 (before: {before_hop_value}, after: {after_hop_value})")
                    discrepancies_found = True
                else:
                    logger.info(f"コマンド {traceroute_command}, ホップ {hop_num}: 合格")

        # 不一致が一つでもあった場合は最終的にエラーを出力
        if discrepancies_found:
            raise AssertionError("一部のTraceroute結果が一致しませんでした。エラーログを確認してください。")
        else:
            logger.info("全てのコマンドとホップが一致しました。試験結果は合格です。")

    @keyword("Compare SR Policy Results")
    def compare_sr_policy_results(self, before_file_path, after_parsed_data):
        with open(before_file_path, 'r') as file:
            before_data = json.load(file)

        # 'after' データを辞書に変換して比較しやすくする
        after_dict = {}
        for item in after_parsed_data:
            for policy, details in item['SR-Policy'].items():
                after_dict[policy] = details

        # 'before' データが期待通りの形式になっていることを確認
        before_dict = {}
        for item in before_data:
            for policy, details in item['SR-Policy'].items():
                before_dict[policy] = details

        # 'before' データにないポリシーや 'after' データにないポリシーを確認
        missing_in_before = set(after_dict.keys()) - set(before_dict.keys())
        missing_in_after = set(before_dict.keys()) - set(after_dict.keys())

        if missing_in_before or missing_in_after:
            message = ""
            if missing_in_before:
                message += f"'before' データに存在しないポリシー: {missing_in_before}。"
            if missing_in_after:
                message += f"'after' データに存在しないポリシー: {missing_in_after}。"
            raise AssertionError(message)

        # 各ポリシーの詳細を比較
        for policy, after_details in after_dict.items():
            before_details = before_dict.get(policy)
            if before_details != after_details:
                raise AssertionError(f"ポリシー '{policy}' に不一致があります: Before={before_details}, After={after_details}")
            else:
                logger.info(f"ポリシー '{policy}' が一致しました。テスト合格。")

        logger.info("全てのSR-Policyの詳細が一致しました。テスト合格。")


    @keyword("Show commands")
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

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CustomKeywords, cls).__new__(cls)
            cls._instance.testbed = None
            cls._instance.devices = []
        return cls._instance

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


    #@keyword("Connect To All Devices")
    def connect_to_all_devices(self):
        for device in self.devices:
            device.connect()
            logger.info(f"Connected to device: {device.name}")
            
    # @keyword("Connect To Some Devices")
    # def connect_to_some_devices(self, devices=None):
    #     if not self.devices:
    #         raise ValueError("Device list is empty. Ensure that the testbed is correctly loaded and devices are accessible.")

    #     if devices:
    #         # デバイス名のリストに基づいて、対象デバイスをフィルタリング
    #         target_devices = [device for device in self.devices if device.name in devices]
    #     else:
    #         # 引数が与えられない場合、すべてのデバイスが対象
    #         target_devices = self.devices
            
    #     for device in target_devices:
    #         device.connect()
    #         logger.info(f"Connected to device: {device.name}")
            
    @keyword("Execute Command Parallel")
    def execute_command_parallel(self, command, devices=None):
        if not self.devices:
            raise ValueError("Device list is empty. Ensure that the testbed is correctly loaded and devices are accessible.")

        if devices:
            # デバイス名のリストに基づいて、対象デバイスをフィルタリング
            target_devices = [device for device in self.devices if device.name in devices]
        else:
            # 引数が与えられない場合、すべてのデバイスが対象
            target_devices = self.devices

        results = []

        def execute_command(device):
            output = device.execute(command)
            device_info = {
                'name': device.name,
                'os': device.os,
                'ip': device.connections.cli.ip,  # デバイスの接続情報に応じて変更する場合があります
                'command_output': output
            }
            return device_info

        with ThreadPoolExecutor(max_workers=len(target_devices)) as executor:
            futures = [executor.submit(execute_command, device) for device in target_devices]
            for future in as_completed(futures):
                results.append(future.result())

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

        # Return the sorted list
        return results

        # # 自然順序でソートするための関数を修正
        # def atoi(text):
        #     return int(text) if text.isdigit() else text

        # def natural_keys(item):
        #     # 辞書の'name'キーを基にして英字と数字で分割し、数字は整数として扱う
        #     return [atoi(c) for c in re.split(r'([A-Za-z]+|\d+)', item['name'])]

        # # resultsをデバイス名の自然順序でソート
        # results.sort(key=natural_keys)
        # デバイス名を非数値部分と数値部分に分割するユーティリティ関数
        # def split_device_name(name):
        #     non_digit_part = ''.join(filter(lambda x: not x.isdigit(), name))
        #     digit_part = ''.join(filter(lambda x: x.isdigit(), name))
        #     return non_digit_part, int(digit_part) if digit_part else 0

        # # カスタム比較関数を用いたソート
        # results.sort(key=lambda x: split_device_name(x['name']))
        # print(results[0]['name'])
        # return results

        #return results
    
    @keyword("Disconnect From All Devices")
    def disconnect_from_all_devices(self):
        for device in self.devices:
            device.disconnect()
            logger.info(f"Disconnected from device: {device.name}")
            
    def save_parsed_output_to_file(self, folder_path, device_name, parsed_output):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_name = f"{device_name}"
        full_path = os.path.join(folder_path, file_name)
        with open(full_path, 'w') as file:
            json.dump(parsed_output, file, indent=2)
        print(f"Saved parsed output to {full_path}")

    @keyword("Parse Command On Selected Devices Parallel")
    def parse_command_on_selected_devices_parallel(self, folder_path, devices, command):
        results = []

        def parse_command(device):
            try:
                parsed_output = device.parse(command)
                # 結果を指定されたフォルダに保存
                self.save_parsed_output_to_file(folder_path, device.name, parsed_output)
                device_info = {
                    'name': device.name,
                    'parsed_output': parsed_output
                }
            except Exception as e:
                device_info = {
                    'name': device.name,
                    'error': str(e)
                }
            return device_info

        selected_devices = [device for device in self.devices if device.name in devices]
        with ThreadPoolExecutor(max_workers=len(selected_devices)) as executor:
            futures = [executor.submit(parse_command, device) for device in selected_devices]
            for future in as_completed(futures):
                results.append(future.result())

        return results