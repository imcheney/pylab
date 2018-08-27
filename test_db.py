# coding:utf-8

import pymongo


def create_db():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["mydb01"]


def list_db():
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    dblist = myclient.list_database_names()
    print dblist
    if "mydb01" in dblist:
        print("数据库已存在！")
    else:
        print 'no'


def create_collection():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["mydb01"]
    mycol = mydb["person"]


def check_collection():
    collist = get_collection()
    print collist
    if "person" in collist:  # 判断 sites 集合是否存在
        print("集合已存在！")
    else:
        print 'no'


def get_collection():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["mydb01"]
    mycol = mydb['person']  # represent a table
    return mycol


def insert_record(record):
    mycol = get_collection()
    x = mycol.insert_one(record)
    print(x)


def find_record(query, sort_param=('age', 1)):
    mycol = get_collection()
    for x in mycol.find(query).sort(*sort_param):  # you can use sort here
        print(x)


def update_record(query, new_value):
    mycol = get_collection()
    mycol.update_one(query, new_value)


def delete_record(query):
    mycol = get_collection()
    mycol.delete_one(query)


def test_update():
    find_record({})
    print '========='
    update_record(query={'name': 'Ling'}, new_value={"$set": {"gender": "female"}})
    print '============'
    find_record({})


def test_delete():  # delete_many且传入空, 可以删除所有的记录
    find_record({})
    print '========='
    delete_record(query={'name': 'Ling'})
    print '============'
    find_record({})


def test_sort():
    find_record({}, sort_param=('age', -1))


if __name__ == '__main__':
    test_sort()