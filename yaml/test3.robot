*** Settings ***
Library        Collections
Library        OperatingSystem
Library        ats.robot.pyATSRobot
Library        genie.libs.robot.GenieRobot
Library        unicon.robot.UniconRobot
Library        CustomKeywords.py    WITH NAME    CustomKeywords
Suite setup    Setup
Suite Teardown  Teardown

*** Variables ***
${testbed}    testbed.yaml
#${check_files_dir}  ./log/test/check_data
#${comparison_files_dir}  ./log/check_data



*** Keywords ***
Setup
    CustomKeywords.Init Testbed   ${testbed}   #${selected_devices}
    CustomKeywords.Connect To All Devices


1.ログ取得
    [Arguments]    ${dummy}

    ${show_commands}  Show commands  ./show
    ${all_results}=    Create List
    
    #@{selected_devices}    Create List    PE1  PE2  P3 P4 PE5  PE6  CE


    FOR    ${command}    IN    @{show_commands}
        ${results}=    Execute Command Parallel    ${command}  #${selected_devices} 
        FOR    ${result}    IN    @{results}
             Log    Output: ${result['command_output']}
        END
    END

Teardown
    CustomKeywords.disconnect from all devices

*** Test Cases ***
1.ログ取得
    [Template]    1.ログ取得
    Start

