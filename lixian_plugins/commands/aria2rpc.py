
from lixian_plugins.api import command

from lixian_config import *
from lixian_encoding import default_encoding
from lixian_cli_parser import command_line_parser
from lixian_cli_parser import with_parser
from lixian_cli_parser import command_line_option, command_line_value
from lixian_commands.util import parse_login, create_client

import urllib2
import json


def get_download_task_info(args, client):

    import lixian_query
    tasks = lixian_query.search_tasks(client, args)
    files = []
    for task in tasks:
        if task['type'] == 'bt':
            subs, skipped, single_file = lixian_query.expand_bt_sub_tasks(task)
            if not subs:
                continue
            if single_file:
                files.append((subs[0]['xunlei_url'], subs[0]['name'], None))
            else:
                for f in subs:
                    files.append((f['xunlei_url'], f['name'], task['name']))
        else:
            files.append((task['xunlei_url'], task['name'], None))
    return files


def export_download_task_info(files, client):
    output = ''
    for url, name, dir in files:
        if type(url) == unicode:
            url = url.encode(default_encoding)
        output += url + '\n'
        output += '  out=' + name.encode(default_encoding) + '\n'
        if dir:
            output += '  dir=' + dir.encode(default_encoding) + '\n'
        output += '  header=Cookie: gdriveid=' + client.get_gdriveid() + '\n'
    return output


def execute_download_aria2rpc(args):
    client = create_client(args)
    task_list = get_download_task_info(args, client)
    # print(export_download_task_info(task_list, client))

    for url, name, dir in task_list:
        if type(url) == unicode:
            url = url.encode(default_encoding)
        if dir:
            dir = dir.encode(default_encoding)

        jsonreq = json.dumps({"jsonrpc": "2.0", "id": "qwer",
                              "method": "aria2.addUri",
                              "params": [
                                         [url],
                                         {
                                             "out": name.encode(default_encoding),
                                             "continue": "true",
                                             "header": ['Cookie: gdriveid=%s' % client.get_gdriveid()]
                                         }
                              ]
                              })
        # print(jsonreq)
        c = urllib2.urlopen("http://127.0.0.1:6800/jsonrpc", jsonreq)
        # {u'jsonrpc': u'2.0', u'id': u'qwer', u'result': u'f1257fa333f235e6'}
        result = c.read()
        if result is None or result == "":
            print("\033[31mCann't add aria2 task %s\033[0m" % name)
        else:
            result = json.loads(result.decode(default_encoding))
            print("\033[32mAdd aria2 task[id=%s] %s\033[0m" % (result[u"result"], name))


@command(usage='concurrently download tasks in aria2 with rpc')
@command_line_parser()
@with_parser(parse_login)
@command_line_option('all')
def download_aria2rpc(args):
    '''
    usage: lx download-aria2rpc -j 5 [id|name]...
    '''
    execute_download_aria2rpc(args)
