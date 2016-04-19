
from lixian_plugins.api import command
from lixian_encoding import default_encoding

from lixian_commands.util import *
from lixian_cli_parser import *
from lixian_config import get_config
import lixian_help
import lixian_query

import urllib2
import json


DEFAULT_JSONRPC = 'http://127.0.0.1:6800/jsonrpc'


@command(usage = r'add tasks to Xunlei cloud and download with aria2rpc')
@command_line_parser()
@with_parser(parse_login)
@with_parser(parse_colors)
@with_parser(parse_logging)
@with_parser(parse_size)
@command_line_value('limit', default=get_config('limit'))
@command_line_value('page-size', default=get_config('page-size'))
@command_line_value('input', alias='i')
@command_line_option('torrent', alias='bt')
def addarpc(args):
    '''
    usage:
        python lixian_cli.py add url
        python lixian_cli.py add 1.torrent
        python lixian_cli.py add torrent-info-hash
        python lixian_cli.py add --bt http://xxx/xxx.torrent
    '''
    assert len(args) or args.input
    client = create_client(args)
    tasks = lixian_query.find_tasks_to_download(client, args)
    print 'All tasks added. Checking status...'
    columns = ['id', 'status', 'name']
    if get_config('n'):
        columns.insert(0, 'n')
    if args.size:
        columns.append('size')
    output_tasks(tasks, columns, args)

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

    for url, name, dir in files:
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
        jsonrpc = get_config('aria2jsonrpc')
        if jsonrpc is None:
            global DEFAULT_JSONRPC
            jsonrpc = DEFAULT_JSONRPC
        c = urllib2.urlopen(jsonrpc, jsonreq)
        result = c.read()
        if result is None or result == "":
            print("\033[31mCann't add aria2 task %s\033[0m" % name)
        else:
            result = json.loads(result.decode(default_encoding))
            print("\033[32mAdd aria2 task[id= %s] %s\033[0m" % (result[u"result"], name))
