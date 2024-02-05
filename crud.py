from datetime import datetime
import psycopg2
import psycopg2.extras
import parameters as gl
import sys


def output_query_many(sql, data=None):
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
        print(str(e), '\n -- SQL Error --\n', 'SQL:' + sql, '\nDATA:', data)
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


def eventos_main(year=2023):
    """
    :param year:
    :return:
    """
    print('eventos main')
    sql = """
        SELECT ev_id,ev_ano, mes_ini.mes_long, ev_dia_inicio, ev_dia_fim,mes_fim.mes_long, ev_nome, ev_local, 
        ev_freguesia, ev_concelho, ev_distrito, ev_novo,ev_arquivo, ev_mes
        from eventos 
        inner join meses mes_ini on ev_mes=mes_id 
        inner join meses as mes_fim on ev_mes_fim=mes_fim.mes_id 
        where ev_ano=%s
        order by ev_ano desc, ev_mes, ev_dia_inicio"""
    eventos_list = output_query_many(sql, (year,))
    return eventos_list

def eventos_novos(year=2023):
    sql = """
        SELECT ev_id,ev_ano, mes_ini.mes_long, ev_dia_inicio, ev_dia_fim,mes_fim.mes_long, ev_nome, ev_local, 
        ev_freguesia, ev_concelho, ev_distrito, ev_novo,ev_arquivo, ev_mes
        from eventos 
        inner join meses mes_ini on ev_mes=mes_id 
        inner join meses as mes_fim on ev_mes_fim=mes_fim.mes_id 
        where ev_ano=%s and ev_novo = True
        order by ev_ano desc, ev_mes, ev_dia_inicio"""
    eventos_list = output_query_many(sql, (year,))
    return eventos_list


def eventos_pesquisa(evento_txt):
    # '\'%' + name.lower() + '%\''
    name = '\'%' + evento_txt.lower() + '%\''
    sql = '''
        SELECT ev_id,ev_ano, mes_ini.mes_long, ev_dia_inicio, ev_dia_fim,mes_fim.mes_long, ev_nome, ev_local, ev_freguesia, ev_concelho, ev_distrito
        , ev_novo,ev_arquivo, ev_mes
        from eventos 
        inner join meses mes_ini on ev_mes=mes_id 
        inner join meses as mes_fim on ev_mes_fim=mes_fim.mes_id 
        where lower(ev_nome) like ''' + name + ''' 
             order by ev_ano desc, ev_mes, ev_dia_inicio'''
    eventos_list = output_query_many(sql)
    return eventos_list


def calendario_main(command='now'):
    if command == 'now':
        data = datetime.now().date()
        y = data.year
        m = data.month
        d = data.day
    if command == 'year':
        data = datetime.now().date()
        y = data.year
        y = gl.current_year
        m = datetime.now().month
        d = 1

    execute_query('delete from eventos_tmp')
    data = datetime.now()
    eventos_tmp = output_query_many(
        'select * from eventos where ev_ano=%s and ev_mes>=%s order by ev_mes, ev_dia_inicio ', (y, m))
    mes_stack = 0
    for n in eventos_tmp:
        if mes_stack == n[2]:
            execute_query('insert into eventos_tmp (select * from eventos where ev_id=%s) ', (n[0],))
            mes_stack = n[2]
        else:
            execute_query('insert into eventos_tmp (ev_ano,ev_mes, ev_mes_fim,ev_nome) values (%s,%s,%s,-1) ',
                          (gl.current_year, n[2], n[4]))
            execute_query('insert into eventos_tmp (select * from eventos where ev_id=%s) ', (n[0],))
            mes_stack = n[2]

    sql = """
        SELECT ev_id,ev_ano, mes_ini.mes_long, ev_dia_inicio, ev_dia_fim,mes_fim.mes_long, ev_nome, ev_local, ev_freguesia, ev_concelho, ev_distrito,
               to_date((ev_ano::text || '-' || ev_mes::text || '-' || ev_dia_fim::text),  'YYYY-MM-DD')  -
        to_date((ev_ano::text || '-' || ev_mes::text || '-' || ev_dia_inicio::text),  'YYYY-MM-DD')as DIFF
        from eventos_tmp 
        inner join meses mes_ini on ev_mes=mes_id 
        inner join meses as mes_fim on ev_mes_fim=mes_fim.mes_id 
        where ev_ano=%s and ev_arquivo = False 
        order by ev_ano desc , ev_mes, ev_dia_inicio """
    eventos_list = output_query_many(sql, (gl.current_year,))
    for n in eventos_list:
        local = n[7]
        freguesia = n[8]
        concelho = n[9]
        distrito = n[10]
        if local == freguesia and local == concelho and local == distrito:
            freguesia = None
            concelho = None
            distrito = None
        if local == freguesia:
            freguesia = None

        if local == distrito:
            distrito = None
        if local == concelho:
            concelho = None

        if freguesia == concelho:
            concelho = None
        if concelho == distrito:
            distrito = None
        execute_query(
            'update eventos_tmp set ev_local=%s, ev_freguesia=%s, ev_concelho=%s, ev_distrito=%s where ev_id =%s',
            (local, freguesia, concelho, distrito, n[0]))
    eventos_list = output_query_many(sql,(gl.current_year,))

    return eventos_list