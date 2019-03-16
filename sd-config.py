#!/usr/bin/env python
#-*- coding:utf-8 -*-

import json
import argparse
import logging
import fileinput
import getpass
# from functools import partial
import yaml
import sys
import os

from abc import ABCMeta, abstractmethod
reload(sys)
sys.setdefaultencoding('utf8')

class SdConfigInvalidKey(RuntimeError):
    def __init__(self, arg):
        self.args = arg

class SdConfigKeyNotFound(RuntimeError):
    def __init__(self, arg):
        self.args = arg

class SdConfig:
    def __init__(self, args):
        self.verbose = args.verbose
        self.cfile = args.file
        self.fmt = args.fmt
        self.config = self.getConfig()
        self.formatMap = {
            "host":      SdConfigFormaterHost(),
            "port":      SdConfigFormaterPort(),
            "user":      SdConfigFormaterUser(),
            "password":  SdConfigFormaterPassword(),
            "database":  SdConfigFormaterDatabase(),
            "mysql":     SdConfigFormaterMysql(),
            "ptdsn":     SdConfigFormaterPtdsn(),
            "mysqldiff": SdConfigFormaterMysqlDiff(),
            "rediscli":  SdConfigFormaterRedisCli(),
            "mongo":     SdConfigFormaterMongo(),
            "ftp":       SdConfigFormaterFtp(),
            "list":      SdConfigFormaterLongList(),
            "l":         SdConfigFormaterShortList(),
        }

    def getConfig(self):
        f = open(self.cfile)
        dohicky = yaml.safe_load(f)
        f.close()
        return dohicky;

    def getConfigItem(self, key):
        if not self.config:
            return None
        cfg = self.config.get(key);
        if not cfg:
            return None
        cfg["key"]  = key
        return cfg

    def getFormater(self, fmt):
        result = None
        if self.formatMap.has_key(fmt):
            result = self.formatMap[fmt]
        else:
            result = SdConfigFormaterDefault(fmt)
        return result

    def getFormatList(self):
        choicesMap = {
            "host": "item-ip",
            "port": "item-port",
            "user": "item-用户名",
            "pass": "item-密码",
            "database": "item-数据库名(仅限mysql,mongo)",
            "mysql": "mysql命令行链接信息: -h{host} -P{port} -u{user} -p{password} [{database}]",
            "ptdsn": "percona-toolkit psd格式: h={host},P={port},u={user},p={password}[,D={database}]",
            "mysqldiff": "mysql-utilities mysqldiff格式: {user}:{password}@{host}:{port}",
            "rediscli": "redis终端客户端: -h {host} -p {port} -a {password}",
            "mongo": "MongoDB shell: --host {host}:{port}[/{database}] [--authenticationDatabase={authenticationDatabase}]",
            "ftp": "ftp链接链接字符串: ftp://{user}:{password}@{host}:{port}",
        }

        result = []
        for fmt in self.formatMap.keys():
            formater = self.formatMap.get(fmt)
            if self.verbose:
                result.append("{}: {}".format(fmt, formater.getDesc()))
            else:
                result.append("{}".format(fmt))
        return result

    def getKeyList(self):
        default_format = "l"
        if self.verbose:
            default_format = "list"
        fmttype = self.fmt or default_format
        result = []
        if self.config:
            for keyname in self.config.keys():
                cfg = self.getConfigItem(keyname)
                formater = self.getFormater(fmttype)
                fmt = formater.getFormat(cfg)
                result.append(fmt.format(**cfg))
        return result

    # @raise SdConfigInvalidKey(key)
    # @raise SdConfigKeyNotFound(key)
    def general(self, key):

        if not key:
            raise SdConfigInvalidKey(key)

        cfg = self.getConfigItem(key)
        if not cfg:
            raise SdConfigKeyNotFound(key)

        formater = self.getFormater(self.fmt or cfg.get("type") or "list")
        fmt = formater.getFormat(cfg)
        return fmt.format(**cfg)


class SdConfigFormater:
    @abstractmethod
    def getFormat(self, cfg):
        pass
    @abstractmethod
    def getDesc(self):
        pass

class SdConfigFormaterDefault:
    def __init__(self, fmt):
        self.fmt = fmt
    def getFormat(self, cfg):
        return self.fmt
    def getDesc(self):
        return ""

class SdConfigFormaterHost:
    def getFormat(self, cfg):
        return "{host}"
    def getDesc(self):
        return "item-ip"

class SdConfigFormaterPort:
    def getFormat(self, cfg):
        return "{port}"
    def getDesc(self):
        return "item-port"

class SdConfigFormaterUser:
    def getFormat(self, cfg):
        return "{user}"
    def getDesc(self):
        return "item-用户名"

class SdConfigFormaterPassword:
    def getFormat(self, cfg):
        return "{password}"
    def getDesc(self):
        return "item-密码"

class SdConfigFormaterDatabase:
    def getFormat(self, cfg):
        return "{database}"
    def getDesc(self):
        return "item-数据库名(仅限mysql,mongo)"

class SdConfigFormaterMysql:
    def getFormat(self, cfg):
        result = "-h{host} -P{port} -u{user} -p{password}"
        if (cfg.get("database")):
            result = " ".join([result, "{database}"])
        return result
    def getDesc(self):
        return "mysql命令行链接信息: -h{host} -P{port} -u{user} -p{password} [{database}]"

class SdConfigFormaterPtdsn:
    def getFormat(self, cfg):
        result = "h={host},P={port},u={user},p={password}"
        if (cfg.get("database")):
            result = ",".join([result, "D={database}"])
        return result
    def getDesc(self):
        return "percona-toolkit psd格式: h={host},P={port},u={user},p={password}[,D={database}]"

class SdConfigFormaterMysqlDiff:
    def getFormat(self, cfg):
        return "{user}:{password}@{host}:{port}"
    def getDesc(self):
        return "mysql-utilities mysqldiff格式: {user}:{password}@{host}:{port}"

class SdConfigFormaterRedisCli:
    def getFormat(self, cfg):
        return "-h {host} -p {port} -a {password}"
    def getDesc(self):
        return "redis终端客户端: -h {host} -p {port} -a {password}"

class SdConfigFormaterMongo:
    def getFormat(self, cfg):
        flist = ["--host {host}:{port}", " -u {user} -p {password}"]
        if (cfg.get("database")):
            flist.insert(1, "/{database}")
        if (cfg.get("authenticationDatabase")):
            flist.append(" --authenticationDatabase={authenticationDatabase}")
        return "".join(flist)
    def getDesc(self):
        return "MongoDB shell: --host {host}:{port}[/{database}] [--authenticationDatabase={authenticationDatabase}]"

class SdConfigFormaterFtp:
    def getFormat(self, cfg):
        return "ftp://{user}:{password}@{host}:{port}"
    def getDesc(self):
        return "ftp链接链接字符串: ftp://{user}:{password}@{host}:{port}"

class SdConfigFormaterLongList:
    def getFormat(self, cfg):
        flist = ["{key:<30} -- "]
        if (cfg.get("user")):
            flist.append("{user}@")
        if (cfg.get("type")):
            flist.append("[{type}]")
        if (cfg.get("host")):
            flist.append("{host}")
        if (cfg.get("port")):
            flist.append(":{port}")
        if (cfg.get("database")):
            flist.append("/{database}")
        return "".join(flist)
    def getDesc(self):
        return "格式列表(详细信息)"

class SdConfigFormaterShortList:
    def getFormat(self, cfg):
        return "{key}"
    def getDesc(self):
        return "格式列表(名字)"

def main():
    parser = argparse.ArgumentParser()
    defaultdir = '/'.join(['/home', getpass.getuser(), '.sd-config'])
    defaultfile = '/'.join([defaultdir, 'config.yml'])
    parser.add_argument("-f", "--file", default=defaultfile,
                        help="配置文件默认:{}".format(defaultfile))
    parser.add_argument("--fmt", help="格式的类型,默认mysql")
    parser.add_argument("--list-fmt", action="store_true", help="输出支持的格式")
    parser.add_argument("-l", "--list", action="store_true", help="输出所有的配置列表")
    parser.add_argument("-v", "--verbose", action="store_true", help="输出更多信息")
    parser.add_argument("-k", "--key", help="配置的标识")

    args = parser.parse_args()
    cfile = args.file
    if not os.path.exists(cfile) and cfile == defaultfile:
        if not os.path.exists(defaultdir):
            os.makedirs(defaultdir)
        open(cfile,"w+").close()

    sdConfig = SdConfig(args)

    if (args.list_fmt):
        formatList = sdConfig.getFormatList()
        for formatitem in formatList:
            print(formatitem)
        return

    if (args.list):
        keyList = sdConfig.getKeyList()
        for keyitem in keyList:
            print(keyitem)
        return

    try:
        print(sdConfig.general(args.key))
    except SdConfigInvalidKey, key:
        sys.stderr.write("error message: 请输入配置标识(key)")
        exit(1)
    except SdConfigKeyNotFound, key:
        sys.stderr.write("error message: 找不到 key:{},请从-l参数的列表选择".format(key))
        exit(1)

if __name__ == "__main__":
    main()
