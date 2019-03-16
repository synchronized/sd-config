# Always provide completions for command line utilities.
#
# Check Fish documentation about completions:
# http://fishshell.com/docs/current/commands.html#complete
#
# If your package doesn't provide any command line utility,
# feel free to remove completions directory from the project.

complete -c "sd-config" -f -d "Config format output"

complete -c "sd-config" -s f -l file -d "配置文件,默认:~/.sd-config/config.yml"

complete -c "sd-config" -f -s h -l help -d "show this help message and exit"
complete -c "sd-config" -f -s l -l list -d "输出所有的配置列表"
complete -c "sd-config" -f -s v -l verbose -d "输出更多信息"
complete -c "sd-config" -f -l list-fmt -d "输出支持的格式"
complete -c "sd-config" -x -l fmt -a "(sd-config --list-fmt)"
complete -c "sd-config" -x -s k -l key -a "(sd-config -l)"
