# sharkfacts
A repo to run a python slash command to share sharkfacts!

# Env Variables
- FACT_FILE - Path to the shark fact file
- BIND_IP - IP to bind the bottle app too
- BIND_PORT - Port to bind the bottle app too
- LOG_TYPE - Three options:
    - STDOUT: Logs to stdout
    - FILE: Logs to a file, requires setting LOG_FILE
    - SYSLOG: Logs to SysLogHandler, /dev/log
- LOG_FILE - If you set LOG_TYPE to FILE, then set a filepath here