import flask
import dbmain
import parameters as gl
import crud

app = flask.Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    # main route
    print('main route')
    try:
        ano = flask.request.form.get('calendar-year')
        gl.current_year = ano
    except KeyError:
        ano = gl.current_year
    if flask.request.method == 'POST':
        print(flask.request.form)
        if not flask.request.form.get('calendar-all-btn') is None:
            eventos_calendar = crud.calendario_main(command='year')
            return flask.render_template('calendar_build.html', eventos_calendar=eventos_calendar,
                                         current_year=gl.current_year)

        elif not flask.request.form.get('nova-btn') is None:
            print('cria novo registo')
            event_record = {'ev_ano': gl.current_year, 'ev_id': dbmain.event_new()}
            return flask.render_template('event_show.html', event_record=event_record, current_year=gl.current_year)

        elif not flask.request.form.get('new-events-btn') is None:
            eventos_list = crud.eventos_novos(gl.current_year)
            return flask.render_template('index.html', eventos_list=eventos_list, current_year=gl.current_year)

        elif not flask.request.form.get('home-btn') is None:
            eventos_list = crud.eventos_main(gl.current_year)
            """ gera o home"""
            return flask.render_template('index.html', eventos_list=eventos_list, current_year=gl.current_year)
        elif not flask.request.form.get('pesquisa') is None:
            print('39')
            eventos_list = crud.eventos_pesquisa(flask.request.form.get('pesquisa'))
            return flask.render_template('index.html', eventos_list=eventos_list, current_year=gl.current_year)

    else:
        eventos_list = crud.eventos_main(gl.current_year)
        return flask.render_template('index.html', eventos_list=eventos_list, current_year=gl.current_year)


@app.route('/show_event/<int:ev_id>', methods=['POST', 'GET'])
def show_event(ev_id):
    print('event id', ev_id)
    if flask.request.method == 'POST':
        # print(request.form)
        try:
            print('GRAVA e  FeCHA')
            var = flask.request.form['ev_close_and_save']
            dbmain.event_save(flask.request.form.to_dict())
        except KeyError:
            pass
        try:
            var = flask.request.form['ev_close']
            print('FECHA Tab')
        except KeyError:
            dbmain.event_save(flask.request.form.to_dict())
        try:
            var = flask.request.form['ev_delete']
            dbmain.execute_query('delete from eventos where ev_id=%s', (ev_id,))
        except KeyError:
            pass
        try:
            var = flask.request.form['ev_clone']
            dbmain.duplicate_record(ev_id)

        except KeyError:
            pass
    event_record = dbmain.get_event_data(ev_id)
    return flask.render_template('event_show.html', event_record=event_record, current_year=gl.current_year)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
