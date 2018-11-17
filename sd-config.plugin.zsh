#!/bin/zsh

currdir=$(cd "$(dirname "$0")";pwd)
export SD_CONFIG_PATH="${currdir}"
alias sd-config="/usr/bin/env python ${currdir}/sd-config"
