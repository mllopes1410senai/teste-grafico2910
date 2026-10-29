from flask import Flask, render_template, request, flash, redirect, url_for, session
import fdb
from flask_bcrypt import Bcrypt
from datetime import date
import pygal, os
from collections import Counter

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'Meu-salario'

# conectar o banco:
host = 'localhost'
database = r'C:\Users\Aluno\Desktop\sprint3-apresentacao-2310-main\SPRINT03.FDB'
user = 'sysdba'
password = 'sysdba'

con = fdb.connect(host=host, database=database, user=user, password=password, )  # conectar o banco

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/grafico')
def grafico():
    cursor = con.cursor()
    cursor.execute("""
        SELECT DATA_MOVIMENTACAO, TIPO, VALOR_TOTAL
        FROM MOVIMENTACAO
        ORDER BY DATA_MOVIMENTACAO
    """)
    resultado = cursor.fetchall()
    cursor.close()

    dados = {}

    for linha in resultado:
        data = linha[0]
        tipo = linha[1]
        valor = linha[2]

        if data not in dados:
            dados[data] = [0, 0]

        if tipo == 0:
            dados[data][0] += valor
        elif tipo == 1:
            dados[data][1] += valor

    datas = sorted(dados.keys())

    receitas = [dados[data][0] for data in datas]
    despesas = [dados[data][1] for data in datas]

    grafico = pygal.Bar(
        style=pygal.style.Style(
            background='transparent',
            plot_background='transparent',
            foreground='#6B7280',
            foreground_strong='#374151',
            foreground_subtle='#DCE8F0',
            colors=['#0D7C4E', '#72D99B'],
            title_font_size=18,
            label_font_size=12,
            major_label_font_size=10,
            legend_font_size=12,
            font_family='Arial',
            opacity=1,
            opacity_hover=0.85
        ),
        height=400,
        show_legend=True,
        show_y_guides=True,
        show_x_guides=False,
        legend_at_bottom=True,
        rounded_bars=3,
        x_label_rotation=0
    )

    grafico.title = 'Receitas x Despesas'
    grafico.x_labels = [
        data.strftime('%d/%m/%Y') for data in datas
    ]

    grafico.add('Receitas', receitas)
    grafico.add('Despesas', despesas)

    caminho = os.path.join('static', 'graficos')
    os.makedirs(caminho, exist_ok=True)

    caminho_svg = os.path.join(caminho, 'grafico.svg')
    grafico.render_to_file(caminho_svg)

    return render_template(
        'index.html',
        svg=url_for('static', filename='graficos/grafico.svg')
    )


if __name__ == '__main__':
    app.run(debug=True)