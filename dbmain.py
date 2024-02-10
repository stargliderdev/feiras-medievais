from flask import Flask, render_template, url_for, request, redirect
# from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import psycopg2
import psycopg2.extras

import crud
import parameters as gl
import sys

app = Flask(__name__)


def output_query_many(sql='', data=None):
    conn_string = "host=192.168.5.100 dbname=mercados user=root  password=masterkey"
    try:
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        if data is None:
            cur.execute(sql)
        else:
            cur.execute(sql, data)
        return cur.fetchall()

    except Exception as e:
        print('\n -- SQL ERROR --\n', str(e), '\n', sql, '\n--------------------------------------')
        sys.exit(1)


def output_query_one(sql='', data=None):
    conn_string = "host=192.168.5.100 dbname=mercados user=root  password=masterkey"
    try:
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        if data is None:
            cur.execute(sql)
        else:
            cur.execute(sql, data)
        a = cur.fetchone()
        cur.close()
        return a[0]
    except Exception as e:
        print('\n -- SQL ERROR --\n', str(e), '\n', sql, '\n--------------------------------------')
        sys.exit(1)


def execute_query(sql, data=None):
    conn_string = "host=192.168.5.100 dbname=mercados user=root  password=masterkey"
    try:
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        if data is None:
            cur.execute(sql)
        else:
            cur.execute(sql, data)
        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(e, sql, 'execute_query', data)
        sys.exit(1)


def event_save(fdi):
    try:
        fdi['ev-arquivo'] == 'True'
    except KeyError:
        fdi['ev-arquivo'] = 'False'
    try:
        fdi['ev-novo'] == 'True'
    except KeyError:
        fdi['ev-novo'] = 'False'
    sql = '''update eventos set
    ev_mes = \'''' + (fdi['ev-mes']) + '''\',  
    ev_ano = \'''' + (fdi['ev-ano']) + '''\',
    ev_dia_inicio = \'''' + (fdi['ev-dia-inicio']) + '''\',  
    ev_mes_fim = \'''' + (fdi['ev-mes-fim']) + '''\',  
    ev_dia_fim = \'''' + (fdi['ev-dia-fim']) + '''\',  
    ev_nome= \'''' + (fdi['ev-nome']) + '''\',
    ev_local= \'''' + (fdi['ev-local']) + '''\',
    ev_tipo= \'''' + (fdi['ev-tipo']) + '''\',
    ev_nome_link= \'''' + (fdi['ev-nome-link']) + '''\',
    ev_freguesia= \'''' + (fdi['ev-freguesia']) + '''\',
    ev_concelho= \'''' + (fdi['ev-concelho']) + '''\',
    ev_local_gps = \'''' + '--' + '''\',
    ev_distrito= \'''' + (fdi['ev-distrito']) + '''\',
    ev_arquivo = \'''' + (fdi['ev-arquivo']) + '''\', 
    ev_novo = \'''' + (fdi['ev-novo']) + '''\' 
    where ev_id =%s '''
    execute_query(sql, (fdi['ev-id'],))


def event_new():
    sql = '''INSERT INTO public.eventos (ev_ano, ev_mes, ev_dia_inicio, ev_mes_fim, ev_dia_fim, ev_nome, ev_local, 
    ev_freguesia, ev_concelho, ev_distrito, ev_maps, ev_nome_link, ev_nome_fb, ev_nome_inst, ev_nome_twit, ev_nome_yt, 
    ev_local_link, ev_ordem, ev_arquivo, ev_local_gps, ev_tipo) 
    VALUES (%s, 1, 1, 1, 1, '--', '--', '--', '--', '--', '--', '--', '--', '--', '--', '--', null, 1, false, null, 
    '--');'''
    execute_query(sql, (gl.current_year,))
    a = output_query_one('select max(ev_id) from eventos')
    return a


def duplicate_record(id):
    sql = '''INSERT INTO public.eventos (ev_ano, ev_mes, ev_dia_inicio, ev_mes_fim, ev_dia_fim, ev_nome, ev_local, 
    ev_freguesia, ev_concelho, ev_distrito, ev_maps, ev_nome_link, ev_nome_fb, ev_nome_inst, ev_nome_twit, ev_nome_yt, 
    ev_local_link, ev_ordem, ev_arquivo, ev_local_gps, ev_tipo) 
    select %s, ev_mes, ev_dia_inicio, ev_mes_fim, ev_dia_fim, ev_nome, ev_local, 
    ev_freguesia, ev_concelho, ev_distrito, ev_maps, ev_nome_link, ev_nome_fb, ev_nome_inst, ev_nome_twit, ev_nome_yt, 
    ev_local_link, ev_ordem, ev_arquivo, ev_local_gps, ev_tipo 
    from eventos where ev_id = %s 
    ;'''
    execute_query(sql, (datetime.now().year, id))
    a = output_query_one('select max(ev_id) from eventos')
    return a


def get_event_data(ev_id):
    conn_string = "host=192.168.5.100 dbname=mercados user=root  password=masterkey"
    conn = psycopg2.connect(conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = '''select *, '' as ev_seo from eventos where ev_id =%s'''
    dict_cur.execute(sql, (ev_id,))
    rec_dic = dict_cur.fetchone()
    dict_cur.close()
    conn.close()
    # create seo entry
    seo = rec_dic["ev_nome"] + '\n' + ' de ' + str(rec_dic['ev_dia_inicio']) + ' a ' + \
          str (rec_dic['ev_dia_fim']) + ' de ' + gl.meses[rec_dic['ev_mes']] + ' \n' + rec_dic['ev_local'] + ', ' +\
          rec_dic['ev_freguesia'] + ', ' + rec_dic['ev_concelho'] + ', ' + rec_dic['ev_distrito']
    rec_dic['ev_seo'] = seo

    return rec_dic


def get_recriadores():
    sql = '''select an_id, an_nome, an_tags, an_pais, an_link from animadores order by an_nome '''
    return crud.output_query_many(sql)


if __name__ == "__main__":
    pass
