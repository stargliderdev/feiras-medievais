#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
import os
import shutil, errno
import pathlib


def make_dir(path):
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)


def backup_data():
    os.system('clear')
    os.system('rm ./DATABASE -Rf')
    os.system('mkdir ./DATABASE')
    current_path = str(pathlib.Path().absolute())
    snap_dir = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    postgresql(current_path + '/DATABASE', 'mercados')
    print('backup to NAS:' + current_path)
    print(current_path + ' 192.168.5.198:/volume1/snapshots/' + snap_dir)
    os.system('rsync --archive --compress --partial ' + current_path + ' 192.168.5.198:/volume1/snapshots/' + snap_dir)
    print('Directoria no NAS:', snap_dir);
    print('Backup terminado');
    # rsync --archive --compress --progress --partial /home/zorze/python/gabo 192.168.5.198:/volume1/snapshots/2022-12-10_1206
    # run_command('rsync -ave ssh --numeric-ids zorze@192.168.0.160:/home/zorze/python /' + disco + '/zorze',disco,'backup')


def snapshot_data(source_path, target_path):
    print(40 * '*')
    print('Make snapshot: ' + source_path + ' --> ' + target_path + datetime.datetime.now().strftime("%Y-%m-%d_%H%M"))
    print(40 * '*')
    toto = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    try:
        shutil.copytree(source_path, target_path + toto)
        # shutil.copytree('c:\\python', 'S:\\'+ toto)
    except OSError as exc:  # python >2.5
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(source_path, target_path + toto)
        else:
            raise


def postgresql(target_path, database):
    print('Fazendo backup do Postgresql --> ' + target_path)
    drive = target_path
    tdate = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    # print('{0:^20}'.format('Database'),'{0:^18}'.format('host'), '{0:^20}'.format('Date'), '{0:^40}'.format('File'))
    # print (110 * '-')
    toto = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    host = 'localhost'
    file_name = drive + '/' + database + '_' + toto + '.backup'
    print('FILE:' + file_name)
    exec_string = 'pg_dump -h ' + host + ' -p 5432 -U root --format custom --blobs --file ' + file_name + ' ' + database
    os.system(exec_string)
    # print (110 * '-')


def main():
    print(' Present Date:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print('File/Dir Name:', datetime.datetime.now().strftime("%Y-%m-%d_%H%M"))
    backup_data()
    print('     End date:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))


main()
