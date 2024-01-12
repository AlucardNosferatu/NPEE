import json
import os
import sys
import threading

from modules.modules_dict import m_dict


def xml_filter(text):
    text = list(text)
    in_label = False
    for i in range(len(text)):
        if text[i] == '<':
            in_label = True
            continue
        elif text[i] == '>':
            in_label = False
        if in_label:
            text[i] = '%'
    text = ''.join(text)
    text = text.replace('%', '').replace('<>', '')
    return text


class FlowChart:
    def __init__(self, prerequisite=None):
        self.hook_script = ''
        self.elements = {}
        self.map_json = None
        self.process_dict = {}
        self.judge_dict = {}
        self.terminal_dict = {}
        self.concurrent_dict = {}
        self.key_map = {}
        self.node_dict = {
            'p': self.process_dict, 'j': self.judge_dict, 't': self.terminal_dict, 'pp': self.concurrent_dict
        }
        self.start_node = ''
        self.current_node = ''
        self.next_link = None
        self.link_list = []
        self.thread_pool = []
        self.params_bus = {'thread_pool': self.thread_pool}
        if prerequisite is not None:
            for key in prerequisite.keys():
                self.params_bus[key] = prerequisite[key]

    def load_map(self, hook_script, map_json='多线程实验.pos'):
        self.hook_script = hook_script
        self.map_json = json.load(
            open(os.path.join('charts', map_json), 'r', encoding='utf-8'))
        self.elements = self.map_json['diagram']['elements']['elements']
        self.reg_links()
        self.find_start()
        self.restart()

    def reg_nodes(self):
        self.link_list.clear()
        for key in self.elements.keys():
            element = self.elements[key]
            if 'name' in element.keys():
                name = element['name']
                if name in ['process', 'decision', 'terminator', 'predefinedProcess']:
                    text = element['textBlock'][0]['text']
                    text = xml_filter(text)
                    if name == 'process':
                        self.process_dict.__setitem__(key, [text])
                        self.key_map.__setitem__(key, ['p'])
                    elif name == 'decision':
                        self.judge_dict.__setitem__(key, [text])
                        self.key_map.__setitem__(key, ['j'])
                    elif name == 'predefinedProcess':
                        self.concurrent_dict.__setitem__(key, [text])
                        self.key_map.__setitem__(key, ['pp'])
                    else:
                        assert name == 'terminator'
                        self.terminal_dict.__setitem__(key, [text])
                        self.key_map.__setitem__(key, ['t'])
                elif name == 'linker':
                    if len(element['textBlock']) > 0:
                        text = element['textBlock'][0]['text']
                        text = xml_filter(text)
                    else:
                        text = None
                    from_node = element['from']['id']
                    to_node = element['to']['id']
                    self.link_list.append([text, from_node, to_node])
                else:
                    raise ValueError(
                        'Only "process", "decision", "terminator" and "linker" are supported.')
            else:
                raise AttributeError(
                    'Attribute "name" is required in JSON nodes.')

    def reg_links(self):
        if len(self.link_list) <= 0:
            self.reg_nodes()
        for link in self.link_list:
            self.reg_link(link[1:], link[0], True)
            self.reg_link(link[1:], link[0], False)

    def reg_link(self, nodes, text, set_from_node=True):
        key_dict_1 = {True: 'to', False: 'from'}
        if set_from_node:
            i, j = 0, 1
        else:
            i, j = 1, 0
        node_info = self.key_map[nodes[i]]
        domain = node_info[0]
        assert domain in self.node_dict.keys()
        self.node_dict[domain][nodes[i]].append(
            {key_dict_1[set_from_node]: [text, nodes[j]]})

    def find_start(self):
        self.start_node = ''
        for key in self.terminal_dict.keys():
            terminal = self.terminal_dict[key]
            is_start = True
            found_next = False
            for i in range(1, len(terminal)):
                link_end = terminal[i]
                direction = list(link_end.keys())[0]
                if direction == 'from':
                    is_start = False
                    break
                elif direction == 'to':
                    if not found_next:
                        found_next = True
                        continue
                    else:
                        raise ValueError(
                            'Terminals should only have 1 next node.')
                else:
                    raise ValueError(
                        'Cannot extract direction info from dict.')
            if is_start:
                if self.start_node == '':
                    self.start_node = key
                else:
                    raise ValueError('Multiple starting nodes detected.')

    def restart(self):
        self.current_node = self.start_node

    def set_node(self, cat, node_id):
        if cat in ['p', 'j', 't']:
            if node_id in self.node_dict[cat].keys():
                self.current_node = node_id
            else:
                print('Cannot find label:', node_id, 'for category:', cat)
        else:
            print('Unrecognized category:', cat)

    def run_step(self):
        cat = self.key_map[self.current_node][0]
        node = self.node_dict[cat][self.current_node]
        next_node = ''
        if cat == 'p':
            module_func = m_dict[node[0]]
            print('现在执行:{}'.format(module_func))
            self.params_bus = module_func(self.params_bus)
        elif cat == 'j':
            switch_dict = {True: None, False: None}
            for switch in node[0].split(','):
                if switch.split(':')[0] == 'T':
                    switch_dict[True] = switch.split(':')[1]
                elif switch.split(':')[0] == 'F':
                    switch_dict[False] = switch.split(':')[1]
                else:
                    raise SyntaxError(
                        'T for True and F for False, other Alphabets are invalid.')
            assert self.params_bus['if_switch'] is not None
            print('现在判断:{}'.format(self.params_bus['if_switch']))
            self.next_link = switch_dict[self.params_bus['if_switch']]
            self.params_bus['if_switch'] = None
        elif cat == 'pp':
            threads = node[0].split(',')
            for thread in threads:
                if thread.startswith('MT:'):
                    self.next_link = thread.replace('MT:', '')
                else:
                    thread = thread.split(':')[1].replace(
                        '[', '').replace(']', '').split('-')
                    thread_func = None
                    hook_text = ''
                    for link in self.link_list:
                        if link[0].split('\n#')[0] == thread[0]:
                            thread_func = m_dict[self.node_dict[self.key_map[link[-1]][0]][link[-1]][0]]
                            hook_text = link[0]
                            break
                    if thread_func is None:
                        raise TypeError(
                            'Cannot find link with name:{}'.format(thread[0]))
                    else:
                        thread_obj = threading.Thread(
                            target=self.serial_execution, args=([hook_text.lower(), thread_func],))
                        print('立刻执行线程{}，线程函数{}'.format(
                            thread_obj, [hook_text.lower(), thread_func]))
                        thread_obj.start()
                        self.thread_pool.append(
                            {
                                'thread_obj': thread_obj,
                                'join_link': thread[1]
                            }
                        )
        elif cat == 't':
            pass
        else:
            raise ValueError('Cannot recognize node category.')

        for i in range(1, len(node)):
            direction = list(node[i].keys())[0]
            if direction == 'from':
                continue
            elif direction == 'to':
                if cat in ['p', 't']:
                    if next_node == '':
                        if node[i][direction][0] is not None:
                            self.execute_hook(
                                hook_text=node[i][direction][0].lower())
                        next_node = node[i][direction][1]
                    else:
                        raise KeyError(
                            'Only 1 next node is allowed for Process & Terminal node.')
                elif cat in ['j', 'pp']:
                    if self.next_link == node[i][direction][0].split('#')[0].strip():
                        if next_node == '':
                            if node[i][direction][0] is not None:
                                self.execute_hook(
                                    hook_text=node[i][direction][0].lower())
                            next_node = node[i][direction][1]
                            self.next_link = None
                        else:
                            raise KeyError('All link name must be unique.')
                    else:
                        continue
                else:
                    raise ValueError('Cannot recognize node category.')
        if len(next_node) > 0:
            self.current_node = next_node
            return False
        else:
            print('End of task.')
            return True

    def serial_execution(self, functions):
        for function in functions:
            if type(function) == str:
                self.params_bus = self.execute_hook(hook_text=function)
            else:
                self.params_bus = function(params=self.params_bus)

    def execute_hook(self, hook_text):
        hook_name = hook_text.split('#')[0].strip()
        print('准备执行hook:{}'.format(hook_name))
        print('hook描述:{}'.format(hook_text))
        join_threads_after = []
        thread_list_tmp = self.thread_pool.copy()
        while len(thread_list_tmp) > 0:
            thread_dict = thread_list_tmp.pop(0)
            join_link = thread_dict['join_link']
            if join_link[:-1].lower() == hook_name:
                if join_link[-1] == 'B':
                    thread_dict['thread_obj'].join()
                    self.thread_pool.remove(thread_dict)
                    print('线程{}已停止于钩子{}前'.format(
                        thread_dict['thread_obj'], hook_name))
                elif join_link[-1] == 'A':
                    join_threads_after.append(thread_dict)
        if os.path.exists('hooks/{}'.format(self.hook_script)):
            # 检查Hook代码文件是否存在，如果存在，再读取，如果不存在，就不处理
            hook_script = self.hook_script.replace('.py', '')
            if os.getcwd() not in sys.path:
                sys.path.append(os.getcwd())
            exec('import hooks.{} as {}'.format(hook_script, hook_script))
            # hooks为存放模块的文件夹名称，hook_script为hook代码的文件名，比如mt_test.py对应hook_script是mt_test
            self.params_bus: dict
            # 参数流水线（总线，类似日本人爱吃的流水素面），模块所有的数据交互都面向这个
            self.params_bus = eval(
                '{}.{}(params=self.params_bus)'.format(hook_script, hook_name))
            # 相当于params=mt_test.hook_name(self.params_bus)
            # Hook修改params里面的内容，增删改后把params返回
        while len(join_threads_after) > 0:
            thread_dict = join_threads_after.pop(0)
            thread_dict['thread_obj'].join()
            self.thread_pool.remove(thread_dict)
            print('线程{}已停止于钩子{}后'.format(thread_dict['thread_obj'], hook_name))
        return self.params_bus


if __name__ == '__main__':
    fc = FlowChart()
    fc.load_map(hook_script='bin_scan.py', map_json='静态测试.pos')
    end = False
    fc.params_bus['project_id'] = 'OW3.0PR5_R231'
    fc.params_bus['product_id'] = 'X30E'
    fc.params_bus['baseline_project'] = 'OW3.0PR5_R221'
    fc.params_bus[
        'bin_url'
    ] = 'http://10.52.16.112:20290/%E5%9B%BD%E5%86%85/X30E-R231/EW_3.0%281%29B11P231_X30E_10231920_install.bin'
    while not end:
        end = fc.run_step()
