*** Settings ***
Library        Collections
Library        OperatingSystem
Library        ats.robot.pyATSRobot
Library        genie.libs.robot.GenieRobot
Library        genie.libs.robot.GenieRobotApis
Library        unicon.robot.UniconRobot
Library        Parse.py
Library        CustomKeywords.py    WITH NAME    CustomKeywords
Suite setup    Setup
Suite Teardown  Teardown

*** Variables ***
${testbed}    testbed.yaml
${check_files_dir}  ./log/test/check_data
${comparison_files_dir}  ./log/check_data



*** Keywords ***
Setup
    #use genie testbed "${testbed}"
    #connect to all devices
    #@{selected_devices}    Create List    PE1  PE2  P7  #PE4  PE5  PE6  P7
    CustomKeywords.Init Testbed   ${testbed}   #${selected_devices}
    CustomKeywords.Connect To All Devices
    #@{selected_devices}    Create List    PE1  PE2  PE3  PE4  PE5  PE6  P7  P8  CE
    #CustomKeywords.Connect To Some Devices 


1.事前ログ取得確認
#    [Arguments]    ${device}  ${COMMAND}
    [Arguments]    ${dummy}

    ${show_commands}  Show commands  ./show
    ${all_results}=    Create List
    
    #@{selected_devices}    Create List    PE1  PE2  PE4  PE5  PE6  P7


    FOR    ${command}    IN    @{show_commands}
        ${results}=    Execute Command Parallel    ${command}  #${selected_devices} 
        FOR    ${result}    IN    @{results}
            # Log    Device: ${result['name']}, OS: ${result['os']}, IP: ${result['ip']}, Output: ${result['command_output']}
             #Log    Device: ${result['name']}  
             Log    Output: ${result['command_output']}
        END
    END


2.プロトコル確認①‗OSPF Neighbors
#    [Arguments]    ${device}
#     ${dict_file_path}=    Catenate    SEPARATOR=    ${comparison_files_dir}/ospf_neighbors/    ${device}
#     ${check}  parse "show ospf neighbor" on device "${device}"
#     Save Data To JSON File  ${check}  ${device}     ${check_files_dir}/ospf_neighbors/
#     Compare OSPF Neighbors Information   ${dict_file_path}    ${check}
    [Arguments]    ${command} 
    @{selected_devices}    Create List    PE1  PE2  PE3  PE4  PE5  PE6  P7  P8
    
    ${folder_path}=  Set Variable  ${comparison_files_dir}/ospf_neighbors/

    ${results}=    Execute Command Parallel    ${command}  ${selected_devices}
    FOR    ${result}    IN    @{results}
        # Log    Device: ${result['name']}, OS: ${result['os']}, IP: ${result['ip']}, Output: ${result['command_output']}
        Log    Device: ${result['name']},Output: ${result['command_output']}
    END


    ${results}=    Parse Command On Selected Devices Parallel  ${folder_path}  ${selected_devices}  ${command}

    FOR    ${result}    IN    @{results}
        Log    Device: ${result['name']}, Parsed Output: ${result['parsed_output']}
        Compare OSPF Neighbors Information   ${folder_path}/${result['name']}  ${result['parsed_output']}
    END

    # FOR    ${device}    IN    @{selected_devices}
    #     ${file_path}=    Catenate    SEPARATOR=    ${folder_path}/    ${device}
    #     Compare OSPF Neighbors Information   ${file_path}  ${result['parsed_output']}
    # END

    #Compare OSPF Neighbors Information   ${folder_path}    ${result['parsed_output']}


2-1.プロトコル確認①_OSPF VRF Neighbors
#    [Arguments]    ${device}
#     ${dict_file_path}=    Catenate    SEPARATOR=    ${comparison_files_dir}/ospf_neighbors/    ${device}
#     ${check}  parse "show ospf vrf all neighbor" on device "${device}"
#     Save Data To JSON File  ${check}  ${device}     ${check_files_dir}/ospf_neighbors/
#     Compare OSPF Neighbors Information   ${dict_file_path}    ${check}

    [Arguments]    ${command} 
    @{selected_devices}    Create List    CE
    
    ${folder_path}=  Set Variable  ${comparison_files_dir}/ospf_neighbors/

    ${results}=    Execute Command Parallel    ${command}  ${selected_devices}
    FOR    ${result}    IN    @{results}
        # Log    Device: ${result['name']}, OS: ${result['os']}, IP: ${result['ip']}, Output: ${result['command_output']}
        Log    Device: ${result['name']},Output: ${result['command_output']}
    END


    ${results}=    Parse Command On Selected Devices Parallel  ${folder_path}  ${selected_devices}  ${command}

    FOR    ${result}    IN    @{results}
        Log    Device: ${result['name']}, Parsed Output: ${result['parsed_output']}
        Compare OSPF Neighbors Information   ${folder_path}/${result['name']}  ${result['parsed_output']}
    END



3.プロトコル確認②_BGP Neighbors
#    [Arguments]    ${device}
#     ${dict_file_path}=    Catenate    SEPARATOR=    ${comparison_files_dir}/bgp_neighbors/    ${device}
#     ${check}  parse "show bgp neighbors" on device "${device}"
#     Save Data To JSON File  ${check}  ${device}     ${check_files_dir}/bgp_neighbors/
#     Compare BGP Neighbors Session State  ${dict_file_path}    ${check}
    [Arguments]    ${command} 
    @{selected_devices}    Create List    PE1  PE2  PE3  PE4  PE5  PE6  P7  P8
    
    ${folder_path}=  Set Variable  ${comparison_files_dir}/bgp_neighbors/

    ${results}=    Execute Command Parallel    ${command}  ${selected_devices}
    FOR    ${result}    IN    @{results}
        # Log    Device: ${result['name']}, OS: ${result['os']}, IP: ${result['ip']}, Output: ${result['command_output']}
        Log    Device: ${result['name']},Output: ${result['command_output']}
    END


    ${results}=    Parse Command On Selected Devices Parallel  ${folder_path}  ${selected_devices}  ${command}

    FOR    ${result}    IN    @{results}
        Log    Device: ${result['name']}, Parsed Output: ${result['parsed_output']}
        Compare BGP Neighbors Session State   ${folder_path}/${result['name']}  ${result['parsed_output']}
    END



4.プロトコル確認③_BGP VRF ALL Neighbors
#    [Arguments]    ${device}
#     ${dict_file_path}=    Catenate    SEPARATOR=    ${comparison_files_dir}/bgp_vrf_neighbors/    ${device}
#     ${check}  parse "show bgp vrf all neighbors" on device "${device}"
#     Save Data To JSON File  ${check}  ${device}     ${check_files_dir}/bgp_vrf_neighbors/
#     Compare BGP Neighbors Session State  ${dict_file_path}    ${check}
    [Arguments]    ${command} 
    @{selected_devices}    Create List    PE1  PE2  PE3  PE4  PE5  PE6 CE
    
    ${folder_path}=  Set Variable  ${comparison_files_dir}/bgp_vrf_neighbors

    ${results}=    Execute Command Parallel    ${command}  ${selected_devices}
    FOR    ${result}    IN    @{results}
        # Log    Device: ${result['name']}, OS: ${result['os']}, IP: ${result['ip']}, Output: ${result['command_output']}
        Log    Device: ${result['name']},Output: ${result['command_output']}
    END


    ${results}=    Parse Command On Selected Devices Parallel  ${folder_path}  ${selected_devices}  ${command}

    FOR    ${result}    IN    @{results}
        Log    Device: ${result['name']}, Parsed Output: ${result['parsed_output']}
        Compare BGP Neighbors Session State   ${folder_path}/${result['name']}  ${result['parsed_output']}
    END


5.広告経路確認①_Route_Check
    # [Arguments]    ${device}
    # ${dict_file_path}=    Catenate    SEPARATOR=    ${comparison_files_dir}/route/    ${device}
    # ${check_route}  parse "show route ipv4" on device "${device}"
    # Save Data To JSON File  ${check_route}  ${device}     ${check_files_dir}/route/
    # Compare Route VRF Information    ${dict_file_path}    ${check_route}
    [Arguments]    ${command} 
    @{selected_devices}    Create List    PE1  PE2  PE3  PE4  PE5  PE6  P7  P8
    
    ${folder_path}=  Set Variable  ${comparison_files_dir}/route

    ${results}=    Execute Command Parallel    ${command}  ${selected_devices}
    FOR    ${result}    IN    @{results}
        # Log    Device: ${result['name']}, OS: ${result['os']}, IP: ${result['ip']}, Output: ${result['command_output']}
        Log    Device: ${result['name']},Output: ${result['command_output']}
    END


    ${results}=    Parse Command On Selected Devices Parallel  ${folder_path}  ${selected_devices}  ${command}

    FOR    ${result}    IN    @{results}
        Log    Device: ${result['name']}, Parsed Output: ${result['parsed_output']}
        Compare Route VRF Information   ${folder_path}/${result['name']}  ${result['parsed_output']}
    END

6.広告経路確認②_Route_VRF_Check
    # [Arguments]    ${device}
    # ${dict_file_path}=    Catenate    SEPARATOR=    ${comparison_files_dir}/route_vrf/    ${device}
    # ${check_route}  parse "show route vrf all ipv4" on device "${device}" 
    # Save Data To JSON File  ${check_route}  ${device}     ${check_files_dir}/route_vrf/
    # Compare Route VRF Information    ${dict_file_path}    ${check_route}

    [Arguments]    ${command} 
    @{selected_devices}    Create List    PE1  PE2  PE3  PE4  PE5  PE6 CE
    
    ${folder_path}=  Set Variable  ${comparison_files_dir}/route_vrf

    ${results}=    Execute Command Parallel    ${command}  ${selected_devices}
    FOR    ${result}    IN    @{results}
        # Log    Device: ${result['name']}, OS: ${result['os']}, IP: ${result['ip']}, Output: ${result['command_output']}
        Log    Device: ${result['name']},Output: ${result['command_output']}
    END


    ${results}=    Parse Command On Selected Devices Parallel  ${folder_path}  ${selected_devices}  ${command}

    FOR    ${result}    IN    @{results}
        Log    Device: ${result['name']}, Parsed Output: ${result['parsed_output']}
        Compare Route VRF Information   ${folder_path}/${result['name']}  ${result['parsed_output']}
    END

7.広告経路確認③_show bgp vpnv4 unicast
    # [Arguments]    ${device}
    # ${dict_file_path}=    Catenate    SEPARATOR=    ${comparison_files_dir}/bgp_vpn4_unicast/    ${device}
    # ${output}=    execute "show bgp vpnv4 unicast" on device "${device}"
    # ${check_route}=   Bgp Vpnv4 Unicast Parse  ${output}
    # Save Data To JSON File  ${check_route}  ${device}     ${check_files_dir}/bgp_vpn4_unicast/
    # Compare BGP VPNv4 Unicast Data    ${dict_file_path}    ${check_route}

    [Arguments]    ${command} 
    @{selected_devices}    Create List    PE1  PE2  PE3  PE4  PE5  PE6 CE
    
    ${folder_path}=  Set Variable  ${comparison_files_dir}/bgp_vpn4_unicast

    ${results}=    Execute Command Parallel    ${command}  ${selected_devices}
    FOR    ${result}    IN    @{results}
        # Log    Device: ${result['name']}, OS: ${result['os']}, IP: ${result['ip']}, Output: ${result['command_output']}
        Log    Device: ${result['name']},Output: ${result['command_output']}
        ${check_route}=   Bgp Vpnv4 Unicast Parse  ${result['command_output']}
        Save Data To JSON File  ${check_route}  ${result['name']}     ${folder_path}
        Compare BGP VPNv4 Unicast Data   ${folder_path}/${result['name']}  ${check_route}
    END


    #${results}=    Parse Command On Selected Devices Parallel  ${folder_path}  ${selected_devices}  ${command}

    # FOR    ${result}    IN    @{results}
    #     Log    Device: ${result['name']}, Parsed Output: ${result['parsed_output']}
    #     Compare Route VRF Information   ${folder_path}/${result['name']}  ${result['parsed_output']}
    # END


8.SR-Policy（ODN）確認
    # [Arguments]    ${device} 
    # ${output}=  execute "show segment-routing traffic-eng policy" on device "${device}"
    # ${parse}=   Parse SR Policy    ${output}
    # ${dict_file_path}=    Catenate    SEPARATOR=    ${comparison_files_dir}/sr_policy/     ${device}
    # Save Data To JSON File   ${parse}   ${device}     ${check_files_dir}/sr_policy/
    # Compare SR Policy Results    ${dict_file_path}    ${parse}

    [Arguments]    ${command} 
    @{selected_devices}    Create List    PE1  PE2  PE3  PE4  PE5  PE6
    
    ${folder_path}=  Set Variable  ${comparison_files_dir}/sr_policy

    ${results}=    Execute Command Parallel    ${command}  ${selected_devices}
    FOR    ${result}    IN    @{results}
        # Log    Device: ${result['name']}, OS: ${result['os']}, IP: ${result['ip']}, Output: ${result['command_output']}
        Log    Device: ${result['name']},Output: ${result['command_output']}
        ${check_route}=   Bgp Vpnv4 Unicast Parse  ${result['command_output']}
        Save Data To JSON File  ${check_route}  ${result['name']}     ${folder_path}
        Compare SR Policy Results   ${folder_path}/${result['name']}  ${check_route}
    END


9.疎通及び経路確認①_PING
    # [Arguments]    ${device}  ${YAML_FILE} 
    # ${ping_data}=    Load Ping Trace Data From Yaml    ${YAML_FILE}
    # ${ping_commands}=    Generate Commands    ${ping_data}  ping
    # ${all_results}=    Create List
    # FOR    ${command}    IN    @{ping_commands}
    #     ${result}=    execute "${command}" on device "${device}"
    #     ${output_with_command}=    Set Variable    ${command}\n${result}
    #     ${parse}=    Parse Ping Results    ${output_with_command}
    #     Append To List    ${all_results}    ${parse}
    # END
    # ${dict_file_path}=    Catenate    SEPARATOR=    ${comparison_files_dir}/ping/     ${device}
    # Save Data To JSON File  ${all_results}   ${device}     ${check_files_dir}/ping/
    # Compare Ping Results    ${dict_file_path}    ${all_results}

    [Arguments]    ${command}  ${YAML_FILE}
    @{selected_devices}    Create List    CE
    ${folder_path}=  Set Variable  ${comparison_files_dir}/ping
    ${ping_data}=    Load Ping Trace Data From Yaml    ${YAML_FILE}
    ${ping_commands}=    Generate Commands    ${ping_data}  ${command}
    ${all_results}=    Create List

    FOR    ${command}    IN    @{ping_commands}
        ${results}=    Execute Command Parallel    ${command}  ${selected_devices}
        FOR    ${result}    IN    @{results}
            # Log    Device: ${result['name']}, OS: ${result['os']}, IP: ${result['ip']}, Output: ${result['command_output']}
            ${output_with_command}=    Set Variable    ${command}\n${result}
            Log    Device: ${result['name']},Output: ${output_with_command}\n${result['command_output']}
            ${parse}=   Parse Ping Results  ${output_with_command}\n${result['command_output']}
            Append To List    ${all_results}    ${parse}
            #Save Data To JSON File  ${check_route}  ${result['name']}     ${folder_path}
            #Compare SR Policy Results   ${folder_path}/${result['name']}  ${check_route}
        END
        Save Data To JSON File  ${all_results}  ${result['name']}     ${folder_path}
        Compare Ping Results   ${folder_path}/${result['name']}  ${all_results}
    END



10.疎通及び経路確認②_traceroute
    # [Arguments]    ${device}  ${YAML_FILE} 
    # ${data}=    Load Ping Trace Data From Yaml    ${YAML_FILE}
    # ${commands}=    Generate Commands    ${data}  traceroute
    # ${all_results}=    Create List
    # FOR    ${command}    IN    @{commands}
    #     ${result}=    execute "${command}" on device "${device}"
    #     ${output_with_command}=    Set Variable    ${command}\n${result}
    #     ${parse}=    Parse Traceroute Results    ${output_with_command}
    #     Append To List    ${all_results}    ${parse}
    # END
    # ${dict_file_path}=    Catenate    SEPARATOR=    ${comparison_files_dir}/traceroute/     ${device}
    # Save Data To JSON File  ${all_results}   ${device}     ${check_files_dir}/traceroute/
    # Compare Traceroute Results    ${dict_file_path}    ${all_results}
    [Arguments]    ${command}  ${YAML_FILE}
    @{selected_devices}    Create List    CE
    ${folder_path}=  Set Variable  ${comparison_files_dir}/traceroute
    ${data}=    Load Ping Trace Data From Yaml    ${YAML_FILE}
    ${commands}=    Generate Commands    ${data}  ${command}
    ${all_results}=    Create List

    FOR    ${command}    IN    @{commands}
        ${results}=    Execute Command Parallel    ${command}  ${selected_devices}
        FOR    ${result}    IN    @{results}
            # Log    Device: ${result['name']}, OS: ${result['os']}, IP: ${result['ip']}, Output: ${result['command_output']}
            ${output_with_command}=    Set Variable    ${command}\n${result}
            Log    Device: ${result['name']},Output: ${output_with_command}\n${result['command_output']}
            ${parse}=   Parse Traceroute Results  ${output_with_command}\n${result['command_output']}
            Append To List    ${all_results}    ${parse}
            #Save Data To JSON File  ${check_route}  ${result['name']}     ${folder_path}
            #Compare SR Policy Results   ${folder_path}/${result['name']}  ${check_route}
        END
        Save Data To JSON File  ${all_results}  ${result['name']}     ${folder_path}
        Compare Traceroute Results   ${folder_path}/${result['name']}  ${all_results}
    END



11.疎通及び経路確認③_SR-PING
    # [Arguments]    ${device}  ${SR_YAML_FILE}

    # ${ping_data}=    Load SR Ping Data From YAML    ${SR_YAML_FILE}  ${device}
    # ${ping_commands}=    Generate SR Commands    ${ping_data}  sr-ping
    # ${all_results}=    Create List
    # FOR    ${command}    IN    @{ping_commands}
    #     ${result}=    execute "${command}" on device "${device}"
    #     ${output_with_command}=    Set Variable    ${command}\n${result}
    #     ${parse}=    Parse Ping Results    ${output_with_command}
    #     Append To List    ${all_results}    ${parse}
    # END
    # ${dict_file_path}=    Catenate    SEPARATOR=    ${comparison_files_dir}/sr_ping/    ${device}
    # Save Data To JSON File  ${all_results}  ${device}     ${check_files_dir}/sr_ping/
    # Compare Ping Results    ${dict_file_path}    ${all_results}

    [Arguments]    ${command_type}  ${YAML_FILE}
    @{selected_devices}    Create List    PE1  PE2   PE3  PE4  PE5  PE6  P7  P8
    ${folder_path}=  Set Variable  ${comparison_files_dir}/sr_ping

    

    FOR  ${selected_device}  IN  @{selected_devices}
        ${ping_data}=    Load SR Ping Data From YAML    ${YAML_FILE}  ${selected_device}
        ${ping_commands}=    Generate SR Commands    ${ping_data}  ${command_type}
        ${all_results}=    Create List

        FOR    ${command}    IN    @{ping_commands}
            ${results}=    Execute Command Parallel    ${command}  ${selected_device}
            FOR    ${result}    IN    @{results}
                # Log    Device: ${result['name']}, OS: ${result['os']}, IP: ${result['ip']}, Output: ${result['command_output']}
                ${output_with_command}=    Set Variable    ${command}\n${result}
                Log    Device: ${result['name']},Output: ${output_with_command}\n${result['command_output']}
                ${parse}=   Parse Ping Results  ${output_with_command}\n${result['command_output']}
                Append To List    ${all_results}    ${parse}
                #Save Data To JSON File  ${check_route}  ${result['name']}     ${folder_path}
                #Compare SR Policy Results   ${folder_path}/${result['name']}  ${check_route}
            END

        END
            Save Data To JSON File  ${all_results}  ${result['name']}     ${folder_path}
            Compare Ping Results   ${folder_path}/${result['name']}  ${all_results}
    END




12.疎通及び経路確認④_SR-Traceroute
    # [Arguments]    ${device}  ${SR_YAML_FILE}

    # ${ping_data}=    Load SR Ping Data From YAML    ${SR_YAML_FILE}  ${device}
    # ${ping_commands}=     Generate SR Commands    ${ping_data}  sr-traceroute
    # ${all_results}=    Create List
    # FOR    ${command}    IN    @{ping_commands}
    #     ${result}=    execute "${command}" on device "${device}"
    #     ${output_with_command}=    Set Variable    ${command}\n${result}
    #     ${parse}=    Parse Traceroute Results    ${output_with_command}
    #     Append To List    ${all_results}    ${parse}
    # END
    # ${dict_file_path}=    Catenate    SEPARATOR=    ${comparison_files_dir}/sr_traceroute/    ${device}
    # Save Data To JSON File  ${all_results}  ${device}     ${check_files_dir}/sr_traceroute/
    # Compare Traceroute Results    ${dict_file_path}    ${all_results}
    [Arguments]    ${command_type}  ${YAML_FILE}
    @{selected_devices}    Create List    PE1  PE2   PE3  PE4  PE5  PE6  P7  P8
    ${folder_path}=  Set Variable  ${comparison_files_dir}/sr_traceroute

    

    FOR  ${selected_device}  IN  @{selected_devices}
        ${data}=    Load SR Ping Data From YAML    ${YAML_FILE}  ${selected_device}
        ${commands}=    Generate SR Commands    ${data}  ${command_type}
        ${all_results}=    Create List

        FOR    ${command}    IN    @{commands}
            ${results}=    Execute Command Parallel    ${command}  ${selected_device}
            FOR    ${result}    IN    @{results}
                # Log    Device: ${result['name']}, OS: ${result['os']}, IP: ${result['ip']}, Output: ${result['command_output']}
                ${output_with_command}=    Set Variable    ${command}\n${result}
                Log    Device: ${result['name']},Output: ${output_with_command}\n${result['command_output']}
                ${parse}=   Parse Traceroute Results  ${output_with_command}\n${result['command_output']}
                Append To List    ${all_results}    ${parse}
                #Save Data To JSON File  ${check_route}  ${result['name']}     ${folder_path}
                #Compare SR Policy Results   ${folder_path}/${result['name']}  ${check_route}
            END

        END
            Save Data To JSON File  ${all_results}  ${result['name']}     ${folder_path}
            Compare Traceroute Results   ${folder_path}/${result['name']}  ${all_results}
    END


Teardown
    CustomKeywords.disconnect from all devices

*** Test Cases ***
1.事前ログ取得確認
    [Tags]  syougai  hukkyuu  10  1
    [Template]    1.事前ログ取得確認
    Start
    #show version
    # PE1
    # PE2
    # PE3
    # PE4
    # PE5
    # PE6
    # P7
    # P8
    # CE

2.プロトコル確認①_OSPF Neighbors
    #Comment  OSPFネイバー状態を確認する
    [Tags]  syougai  hukkyuu  parse  10
    [Template]    2.プロトコル確認①‗OSPF Neighbors
    show ospf neighbor 
    # PE1
    # PE2
    # PE3
    # PE4
    # PE5
    # PE6
    # P7
    # P8

2-1.プロトコル確認①_OSPF VRF Neighbors
    #Comment  OSPFネイバー状態を確認する
    [Tags]  syougai  hukkyuu  5  
    [Template]    2-1.プロトコル確認①_OSPF VRF Neighbors
    show ospf vrf all neighbor
    # CE


3.プロトコル確認②_BGP Neighbors
    #Comment  BGPネイバー状態を確認する
    [Tags]  syougai  hukkyuu  
    [Template]    3.プロトコル確認②_BGP Neighbors
    show bgp neighbors
    # PE1
    # PE2
    # PE3
    # PE4
    # PE5
    # PE6
    # P7
    # P8

4.プロトコル確認③_BGP VRF ALL Neighbors
    #Comment  BGPネイバー状態を確認する(VRF)
    [Tags]  syougai  hukkyuu
    [Template]    4.プロトコル確認③_BGP VRF ALL Neighbors
    show bgp vrf all neighbors
    # PE1
    # PE2
    # PE3
    # PE4
    # PE5
    # PE6
    # CE

5.広告経路確認①_Route_Check
    #Comment  想定される経路とネクストホップおよびバックアップパスの有無(!)を確認する。
    # 比較データは各検証時の構成で事前に取得してJSON形式でファイル化する
    # 検証時に同様の方法で情報を取得して、以下要素で比較する。
    # 想定される経路：          routesの値を確認
    # ネクストホップ：          next_hop_listがある場合は、'source_protocol_codes': 'L'　または、「'C'」以外であることを確認し、viaで記載されるネクストホップのIPを比較。
    # 　　　　　　　　          next_hop_listがない場合は、'source_protocol_codes': 'L'　または、「'C'」であることを確認する。
    # バックアップパスの有無：   バックアップパスの有「'source_protocol_codes': 'O'」無し「'O (!)'」であることを確認する。

    [Tags]  newtest 
    [Template]    5.広告経路確認①_Route_Check
    show route ipv4
    # PE1
    # PE2
    # PE3
    # PE4
    # PE5
    # PE6
    # P7
    # P8

6.広告経路確認②_Route_VRF_Check
    # 比較データは各検証時の構成で事前に取得してJSON形式でファイル化する
    # 検証時に同様の方法で情報を取得して、以下要素で比較する。
    # 想定される経路：          それぞれのvrf内にあるroutesの値を確認
    # ネクストホップ：          next_hop_listがある場合は、'source_protocol_codes': 'L'　または、「'C'」以外であることを確認し、viaで記載されるネクストホップのIPを比較。
    # 　　　　　　　　          next_hop_listがない場合は、'source_protocol_codes': 'L'　または、「'C'」であることを確認する。
    # バックアップパスの有無：   バックアップパスの有「'source_protocol_codes': 'O'」無し「'O (!)'」であることを確認する。

    [Tags]  newtest
    [Template]    6.広告経路確認②_Route_VRF_Check
    show route vrf all ipv4
    # PE1
    # PE2
    # PE3
    # PE4
    # PE5
    # PE6
    # CE

7.広告経路確認③_show bgp vpnv4 unicast
    [Tags]  newtest
    [Template]    7.広告経路確認③_show bgp vpnv4 unicast
    show bgp vpnv4 unicast
    # PE1
    # PE2
    # PE3
    # PE4
    # PE5
    # PE6
    # CE

8.SR-Policy（ODN）確認
    [Tags]  newtest
    [Template]    8.SR-Policy（ODN）確認
    show segment-routing traffic-eng policy
    # PE1
    # PE2
    # PE3
    # PE4
    # PE5
    # PE6


9.疎通及び経路確認①_PING
    [Tags]  syougai  hukkyuu
    [Template]    9.疎通及び経路確認①_PING
    # CE  ping_trace_data.yaml
    ping  ping_trace_data.yaml

10.疎通及び経路確認②_traceroute
    [Tags]  syougai  hukkyuu
    [Template]    10.疎通及び経路確認②_traceroute
    # CE  ping_trace_data.yaml
    traceroute  ping_trace_data.yaml

11.疎通及び経路確認③_SR-PING
    [Tags]  newtest 
    [Template]    11.疎通及び経路確認③_SR-PING
    sr-ping  sr_ping_trace_data.yaml
    # PE1  sr_ping_trace_data.yaml
    # PE2  sr_ping_trace_data.yaml
    # PE3  sr_ping_trace_data.yaml
    # PE4  sr_ping_trace_data.yaml
    # PE5  sr_ping_trace_data.yaml
    # PE6  sr_ping_trace_data.yaml
    # P7   sr_ping_trace_data.yaml
    # P8   sr_ping_trace_data.yaml

12.疎通及び経路確認④_SR-Traceroute
    [Tags]  newtest  6
    [Template]    12.疎通及び経路確認④_SR-Traceroute
    sr-traceroute  sr_ping_trace_data.yaml
    # PE1  sr_ping_trace_data.yaml
    # PE2  sr_ping_trace_data.yaml
    # PE3  sr_ping_trace_data.yaml
    # PE4  sr_ping_trace_data.yaml
    # PE5  sr_ping_trace_data.yaml
    # PE6  sr_ping_trace_data.yaml
    # P7   sr_ping_trace_data.yaml
    # P8   sr_ping_trace_data.yaml
