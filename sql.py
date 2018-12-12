#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/25 08:12
# @Author  : lurkerzhang
# @File    : sql.py
# @Descript: 员工信息增删改查程序，须支持如下语法：
#            1.find name,age from staff_table where age > 22
#            2.find * from staff_table where dept = "IT"
#            3.find * from staff_table where enroll_date like "2013"
#            4.add staff_table Alex Li,25,134435344,IT,2015‐10‐29
#            5.del from staff_table where id=3
#            6.UPDATE staff_table SET dept="Market" WHERE dept = "IT" 把所有dept=IT的纪录的dept改成Market
#            7.UPDATE staff_table SET age=25 WHERE name = "Alex Li" 把name=Alex Li的纪录的年龄改成25
#            注：以上每条语名执行完毕后，要显示这条语句影响了多少条纪录。 比如查询语句 就显示 查询出了多少条、
#            修改语句就显示修改了多少条等。
import os


# 连接数据文件（数据表）
def collect_table(table_name):
    try:
        table = []
        with open(table_name, 'r', encoding='utf-8') as t:
            for r in t:
                r = r.strip().split(',')
                r[0], r[2] = int(r[0]), int(r[2])
                table.append(r)
            return table
    except IOError:
        print('操作的数据表不存在')
        return None


# 定义员工数据表头
def table_header():
    return ['id', 'name', 'age', 'phone', 'dept', 'enroll_date']


# 定义sql语句类别
def sql_types():
    return ['find', 'add', 'update', 'del']


# 定义sql语句关键词
def sql_keywords():
    return ['find', 'add', 'update', 'del', 'where', 'set', 'like']


# 将sql语句关键字变成小写
def list_lower(l):
    l_lower = []
    for i in l:
        if isinstance(i, str) and i.lower() in sql_keywords():
            i = i.lower()
        l_lower.append(i)
    return l_lower


# sql语句结构化字典(find,add,update,del)
def sql_to_dic(sql):
    sql_list = list(filter(None, list_lower(sql.split(' '))))
    # 添加where默认，支持find * from staff_table语句查询所有数据
    if sql_list[0] == 'find' and 'where' not in sql_list:
        sql_list.extend(['where', '', ''])
    # 定义find语句结构的关键字
    find_dic = {
        'type': sql_find,
        'k1': 'find',
        'k2': 'from',
        'k3': 'where',
    }
    # 定义add语句结构的关键字
    add_dic = {
        'type': sql_add,
        'k1': 'add',
        'k2': 'line',
    }
    # 定义update语句结构的关键字
    update_dic = {
        'type': sql_update,
        'k1': 'update',
        'k2': 'set',
        'k3': 'where',
    }
    # 定del语名的关键字
    del_dic = {
        'type': sql_del,
        'k1': 'del',
        'k2': 'from',
        'k3': 'where',
    }

    sql_type = sql_classify(sql)
    try:
        sql_struct = eval('{0}_dic'.format(sql_type))
    except:
        print('语法错误')
        return 0
    sql_dic = {}
    try:
        if sql_type:
            # 根据定义的不同类型的sql语句结构组装成sql语句成字典
            if sql_type == 'add':
                sql_dic = {
                    'sql_exec': sql_struct['type'],
                    sql_struct['k1']: ' '.join(sql_list[1:2]),
                    sql_struct['k2']: (' '.join(sql_list[2:])),
                }
            else:
                # 获取sql语句关键字段的切片位置
                k1_l, k1_r = 1, sql_list.index(sql_struct['k2'])
                k2_l, k2_r = sql_list.index(sql_struct['k2']) + 1, sql_list.index(sql_struct['k3'])
                k3_l = sql_list.index(sql_struct['k3']) + 1
                # 结构化sql语句为字典
                k1_val = sql_list[k1_l:k1_r]
                k1_val = ' '.join(k1_val).strip()
                k2_val = sql_list[k2_l:k2_r]
                k2_val = ' '.join(k2_val).strip()
                k3_val = sql_list[k3_l:]
                k3_val = ' '.join(k3_val).strip()
                sql_dic = {
                    'sql_exec': sql_struct['type'],
                    sql_struct['k1']: k1_val,
                    sql_struct['k2']: k2_val,
                    sql_struct['k3']: k3_val,
                }
        return sql_dic
    except:
        print('语法错误1')
        return 0


# where字段转换成列表
def parse_to_list(where_s):
    cal = ['>', '<', '=', '>=', '<=', 'like']
    l = []
    for i in cal:
        if i in where_s:
            l = where_s.split(i)
            l.insert(1, i)
    where_l = []
    for i in l:
        i = i.strip()
        where_l.append(i)
    return where_l


# 解析匹配where字段,满足条件返回True,否则返回False
def match_where(where_s, line_l):
    line_dic = dict(zip(table_header(), line_l))
    # 将where字段转换成python语句where_excec
    where_l = parse_to_list(where_s)
    try:
        where_l[0] = "line_dic['%s']" % where_l[0]
    except:
        return 0
    where_exec = ''
    if where_l[1] == 'like':
        # 如果是like语法，将比较值都转小写，提高模糊查询精度
        where_exec = ' '.join(["'%s'" % str(where_l[2]).lower(), 'in', "'%s'" % eval(where_l[0]).lower()])
    elif where_l[1] == '=':
        if not where_l[2].isdigit():
            where_l[2] = "'%s'" % where_l[2]
            where_exec = ' '.join([where_l[0], '==', where_l[2]])
        else:
            where_l[2] = "%s" % where_l[2]
            where_exec = ' '.join([where_l[0], '==', where_l[2]])
    elif where_l[1] in ['>', '<', '>=', '<=']:
        where_exec = ' '.join(where_l)
    else:
        return False
    return eval(where_exec)


# 判断sql语句类别：find,add,update,del
def sql_classify(sql):
    s = sql.split(' ')
    if s[0].lower() in sql_types():
        return s[0].lower()
    else:
        return False


# 判断phone值是否重复
def is_phone_unique(table, phone):
    is_unique = True
    for i in table:
        if i[3] == str(phone):
            is_unique = False
    return is_unique


# 操作结果显示
def show_result(res):
    if res:
        print('%s%s' % (res['result'], res['record']))
    else:
        print('操作失败')


# 查询数据
def sql_find(sql_dic):
    rt, rd = '', ''
    table = collect_table(sql_dic['from'])
    # 格式化修改字段
    while_s = format_s(sql_dic['where'])
    if not table:
        return False
    find_l = []
    record = 0
    sql_dic['find'] = sql_dic['find'].replace(' ', '').split(',')
    sql_dic['find'] = table_header() if sql_dic['find'] == ['*'] else sql_dic['find']
    for i in table:
        try:
            if not while_s:
                j = dict(zip(table_header(), i))
                find_l.append(j)
                record += 1
            else:
                if match_where(while_s, i):
                    j = dict(zip(table_header(), i))
                    find_l.append(j)
                    record += 1
        except:
            rt = '未查询到符合条件的记录'
            rd = ''
    if find_l:
        head = ''
        for i in sql_dic['find']:
            head = head + '{:^15}'.format(i)
        print(head)
        for i in find_l:
            line = ''
            for k in sql_dic['find']:
                i[k] = str(i[k]) if isinstance(i[k], int) else i[k]
                line = line + '{:^15}'.format(i[k])
            print(line)
        rt = '查询成功!'
        rd = '查询到符合条件的记录%s条' % record
    else:
        rt = '未查询到符合条件的记录'
        rd = ''
    return {'result': rt, 'record': rd}


# 增加数据
def sql_add(sql_dic):
    rt, rd = '', ''
    table = collect_table(sql_dic['add'])
    if not table:
        rt = '数据表操作错误'
        rd = ''
    else:
        line = sql_dic['line'].split(',')
        if is_phone_unique(table, line[2]):
            with open(sql_dic['add'], 'a', encoding='utf-8') as t:
                line.insert(0, len(table) + 1)
                t.write('\n' + ','.join(list(map(lambda j: str(j) if isinstance(j, int) else j, line))))
                rt = '增加成功!'
                rd = '成功增加1条记录'
        else:
            rt = '增加失败!'
            rd = '电话号码重复'
    return {'result': rt, 'record': rd}


# 改数据
def sql_update(sql_dic):
    # 修改结果变量
    rt, rd = '', ''
    record = 0
    table = collect_table(sql_dic['update'])
    if not table:
        return False
    else:
        # 格式化修改字段
        while_s = format_s(sql_dic['where'])
        set_l = parse_to_list(sql_dic['set'])
        set_l[2] = format_s(set_l[2])
        set_l[2] = int(set_l[2]) if set_l[2].isdigit() else set_l[2]
        # 如果修改的是phone字段，判断phone是否重复
        if set_l[0] == 'phone' and not is_phone_unique(table, set_l[2]):
            rt = '修改失败，电话号码已存在数据表中不能重复'
            rd = ''
        else:
            index = (table_header().index(set_l[0]))  # 获取数据行要修改的位置
            count = 0
            try:
                with open('new', 'w', encoding='utf-8') as f:
                    for i in table:
                        count += 1
                        if match_where(while_s, i):
                            i[index] = set_l[2]
                            write_to_file(i, f)
                            record += 1
                            if count < len(table):
                                f.write('\n')
                        else:
                            write_to_file(i, f)
                            if count < len(table):
                                f.write('\n')
                # 判断如果修改的是phone,修改记录大于1条，禁止保存
                if set_l[0] == 'phone' and record > 1:
                    rt = '修改失败!修改的记录大于1条，号码重复，禁止修改'
                    rd = ''
                elif record == 0:
                    rt = '修改失败!'
                    rd = '符合条件的数据为0'
                else:
                    rt = '修改成功!'
                    rd = '修改数据%s条' % record
                    os.replace('new', 'staff_table')

            except:
                rt = '语法错误！'
                rd = ''

    return {'result': rt, 'record': rd}


# 删数据
def sql_del(sql_dic):
    rt, rd = '', ''
    record = 0
    table = collect_table(sql_dic['from'])
    while_s = format_s(sql_dic['where'])
    if not table:
        return False
    else:
        count = 0
        new_id = 1
        with open('new', 'w', encoding='utf-8') as f:
            for i in table:
                count += 1
                if match_where(while_s, i):
                    record += 1
                else:
                    i[0] = new_id
                    write_to_file(i, f)
                    if count < len(table):
                        f.write('\n')
                    new_id += 1
    if record == 0:
        rt = '删除失败！未找到符合条件的数据'
        rd = ''
    else:
        rt = '删除成功！'
        rd = '删除数据%s条,数据表ID已重新排序' % record
        os.replace('new', 'staff_table')
    return {'result': rt, 'record': rd}


# 格式化字符串
def format_s(s):
    return s.replace('\'', '').replace('\"', '').strip()


# 把数据列写到文件
def write_to_file(i, f):
    f.write(','.join(list(map(lambda j: str(j) if isinstance(j, int) else j, i))))

# 为测试打印的语句示例
def test_sql():
    sqls = '''    ----------------测试语句示例------------
    1.find * from staff_table
    2.find name,age from staff_table where age> 22
    3.find * from staff_table where dept ="IT"
    4.find * from staff_table  where enroll_date like "2013"
    5.add staff_table Alex Li,25,134435344,IT,2015‐10‐29
    6.del from staff_table where id=3
    7.UPDATE staff_table SET dept="Market" WHERE dept = "IT"
    8.UPDATE staff_table SET age=25 WHERE name ="Alex Li"
    ----------------------------------------'''
    print(sqls)

def main():
    test_sql()
    while True:
        sql = input("请输入sql语句(输入'Q'退出)>>>")
        if sql.strip() in ['q', 'Q']:
            exit('bye')
        else:
            sql_dic = sql_to_dic(sql)
            if sql_dic:
                result = sql_dic['sql_exec'](sql_dic)
                show_result(result)


if __name__ == '__main__':
    main()
