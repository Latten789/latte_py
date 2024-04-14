from genie.utils.dq import Dq
from robot.api.deco import keyword
import re
from re import compile, MULTILINE, search
import json

class Parse:

    @keyword("Bgp Vpnv4 Unicast Parse")
    def bgp_vpnv4_unicast_parse(self, data):
        rd_pattern = re.compile(r'Route Distinguisher: (.+)$')
        network_next_hop_pattern = re.compile(r'(.{3})([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/\d+)\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)')
        next_hop_only_pattern = re.compile(r'(.{3})\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)')
        color_pattern = re.compile(r'C:(\d+)')

        results = {}
        last_network = None
        current_rd = None

        for line in data.splitlines():
            if 'Route Distinguisher Version:' in line:
                continue

            rd_match = rd_pattern.search(line)
            if rd_match:
                current_rd = "Route Distinguisher: " + rd_match.group(1)
                results[current_rd] = []
                continue

            if current_rd:
                match = network_next_hop_pattern.search(line)
                if match:
                    last_network = match.group(2)
                    best_path_info = match.group(1)
                    next_hop = match.group(3)
                else:
                    match = next_hop_only_pattern.search(line)
                    if match:
                        best_path_info = match.group(1)
                        next_hop = match.group(2)
                    else:
                        continue

                color_match = color_pattern.search(line)
                entry = {
                    'Best Path Info': best_path_info,
                    'Network': last_network if last_network else "N/A",  # 省略された場合、前のネットワークを使用
                    'Next Hop': next_hop
                }
                if color_match:
                    entry['Color'] = color_match.group(1)
                results[current_rd].append(entry)

        return results

    @keyword("Parse Ping Results")
    def parse_ping_results(self, output_with_command):
        # Ping コマンドと SR-Ping コマンドの正規表現パターン
        ping_command_pattern = compile(r'(ping vrf \S+ \S+ source \S+.*)')
        sr_ping_command_pattern = compile(r'(ping sr-mpls \S+ source \S+.*)')
        success_rate_pattern = compile(r'Success rate is (\d+) percent.*', MULTILINE)

        # 出力からコマンドラインを探す
        if "sr-mpls" in output_with_command:
            command_match = sr_ping_command_pattern.search(output_with_command)
        else:
            command_match = ping_command_pattern.search(output_with_command)
        
        if not command_match:
            raise ValueError("No ping command found in the output.")

        # コマンドライン全体を抜き出し
        ping_command = command_match.group(1)

        # 出力から成功率を探す
        success_rate_match = success_rate_pattern.search(output_with_command)
        if not success_rate_match:
            raise ValueError("No success rate found in the output.")

        return {
            "PING": {
                ping_command: {
                    "Success Rate": success_rate_match.group(1)
                }
            }
        }
    @keyword("Parse Traceroute Results")
    def parse_traceroute_results(self, output_with_command):
        # 'sr-mpls' コマンドを含む場合のパターン
        if 'sr-mpls' in output_with_command:
            traceroute_command_pattern = re.compile(r'(traceroute sr-mpls \S+ source \S+.*)')
            # ホップ情報を正しくキャプチャするために正規表現を修正
            hop_pattern = re.compile(
                r'^(?:\s{2}|.{2})\s*(\d+)\s+([\d\.]+).*?(\d+)\s+ms',  # IPアドレスと応答時間（ms）をキャプチャ
                re.MULTILINE
            )
        else:
            # 'vrf' コマンドを含む場合のパターン
            traceroute_command_pattern = re.compile(r'(traceroute vrf \S+ \S+ source \S+.*)')
            hop_pattern = re.compile(
                r'^\s*(\d+)\s+((?:[\d\.]+|\*\s*\*\s*\*))+.*', 
                re.MULTILINE
            )

        command_match = traceroute_command_pattern.search(output_with_command)
        if not command_match:
            raise ValueError("No traceroute command found in the output.")
        traceroute_command = command_match.group(1)

        hops = {}
        for hop_match in hop_pattern.finditer(output_with_command):
            hop_number = hop_match.group(1)
            hop_info = hop_match.group(2)
            hops[hop_number] = hop_info

        return {
            "Traceroute": {
                traceroute_command: hops
            }
        }

    @keyword("Parse SR Policy")
    def parse_sr_policy(self, data):
        # Regular expression pattern to capture the policy details
        policy_pattern = re.compile(
            r'Color: (\d+), End-point: (\S+)\s+Name: (\S+)\s+Status:\s+Admin: (\S+)\s+Operational: (\S+)',
            re.MULTILINE | re.DOTALL
        )

        policies = []

        for match in policy_pattern.finditer(data):
            color, endpoint, name, admin_status, operational_status = match.groups()
            policy_key = f"Color: {color}, End-point: {endpoint}"
            policy_info = {
                "Admin": admin_status,
                "Operational": operational_status
            }

            policies.append({
                "SR-Policy": {
                    policy_key: policy_info
                }
            })

        return policies