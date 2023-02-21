*** Settings ***
Resource            common.robot
Library             login_utils.py


*** Keywords ***
Open Browser To Login Page
    [Arguments]     ${endpoint}=dashboard/auth/login
    ...             ${timeout}=${BROWSER_WAIT_TIMEOUT}

    Set Default Browser Download Path   ${BROWSER_DOWNLOAD_PATH}
    Open Browser    ${LOGIN URL}/${endpoint}    ${BROWSER}
    ...             options=add_argument("--ignore-certificate-errors"); add_argument("--start-maximized"); add_experimental_option("prefs", {"download.default_directory": "${BROWSER_DOWNLOAD_PATH}"})
    Wait Until Location Contains     ${endpoint}    timeout=${timeout}
    Wait Until Element Is Not Visible   css:i.initial-load-spinner  timeout=${timeout}
    Title Should Be    Harvester
    Log Location

Input Login Username
    [Arguments]    ${username}
    Input Text      css:#username
    ...             ${username}

Input Login Password
    [Arguments]    ${password}
    Input Text      css:#password input
    ...             ${password}

Submit Credentials
    Click Button    css:button[type=submit]

Harvester Dashboard Should Be Display
    Wait Until Location Does Not Contain    auth/login
    ...                                     timeout=${BROWSER_WAIT_TIMEOUT}
    Location Should Contain     harvesterhci.io.dashboard
    Wait Until Element Is Visible   css:main div.outlet   ${BROWSER_WAIT_TIMEOUT}

Login to Harvester Dashboard
    Given Open Browser To Login Page
          Input Login Username    ${HARVESTER_USERNAME}
          Input Login Password    ${HARVESTER_PASSWORD}
    And Submit Credentials
    Then Harvester Dashboard Should Be Display
