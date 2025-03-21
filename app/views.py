import time
from flask import render_template, flash, redirect, g, url_for, session, request, jsonify


from app import app
import pandas as pd
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from .file import file

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    f = file()
    dt = f.walk(f.dirs)
    msg = "先上传商务通和各搜索引擎的导出数据"


    if request.method == 'POST':
        if request.form.get('analysis'):
            is_swt = True if dt['swt'][0] == f.error_exist else False
            if is_swt:
                msg = "没有商务通数据哦"
            else:
                return redirect(url_for('data'))
        elif request.form.get('upload'):
            f.upload(f.dirs)
            return redirect(url_for('index'))
    if request.args.get('clear'):
            f.walk(f.dirs, clear='yes')
            return jsonify("yes")
    flash(msg)
    return render_template('index.html',
                           now=int(time.time()),
                           dt=dt
                           )




@app.route('/data', methods=['GET', 'POST'])
def data():
    f = file()
    dt = f.walk(f.dirs)
    is_swt = True if dt['swt'][0] == f.error_exist else False
    is_baidu = True if dt['baidu'][0] == f.error_exist else False
    is_sogou = True if dt['sogou'][0] == f.error_exist else False
    is_shenma = True if dt['shenma'][0] == f.error_exist else False
    is_360 = True if dt['360'][0] == f.error_exist else False
    #如果没有上传商务通表，则跳转首页
    if is_swt:
        return redirect(url_for('index'))
    else:
        f.read_swt = f.read_swts()
    #如果没有上传搜索引擎的表，则自定义一个dataframe
    if is_baidu:
        baidu_account = pd.DataFrame({'账户':'0','展现':0.0, '点击':0.0,'消费':0.0,'对话':0.0, '转出': 0.0, '有效': 0.0},index=['百度汇总'])
        baidu_plan = baidu_account
    else:
        baidu_account = f.read_baidu()['account']
        baidu_plan = f.read_baidu()['plan']

    if is_sogou:
        sogou_account = pd.DataFrame({'账户':'0','展现':0.0, '点击':0.0,'消费':0.0,'对话':0.0, '转出':0.0, '有效': 0.0},index=['搜狗汇总'])
        sogou_plan = sogou_account
    else:
        sogou_account = f.read_sogou()['account']
        sogou_plan = f.read_sogou()['plan']

    if is_shenma:
        shenma_account = pd.DataFrame({'账户':'0','展现':0.0, '点击':0.0,'消费':0.0,'对话':0.0, '转出':0.0, '有效': 0.0},index=['神马汇总'])
        shenma_plan = shenma_account
    else:
        shenma_account = f.read_shenma()['account']
        shenma_plan = f.read_shenma()['plan']

    if is_360:
        d360_account = pd.DataFrame({'账户':'0','展现':0.0, '点击':0.0,'消费':0.0,'对话':0.0, '转出':0.0, '有效': 0.0},index=['360汇总'])
        d360_plan = d360_account
    else:
        d360_account = f.read_360()['account']
        d360_plan = f.read_360()['plan']


    hz_account = pd.DataFrame([baidu_account.loc['百度汇总'],sogou_account.loc['搜狗汇总'],shenma_account.loc['神马汇总'],d360_account.loc['360汇总']])
    hz_account.loc['大汇总'] = hz_account[['展现', '点击', '消费', '对话', '转出', '有效']].apply(lambda x: x.sum())
    hz_account = hz_account.fillna('0')

    hz_plan = pd.DataFrame([baidu_plan.loc['百度汇总'],sogou_plan.loc['搜狗汇总'],shenma_plan.loc['神马汇总'],d360_plan.loc['360汇总']])
    hz_plan.loc['大汇总'] = hz_plan[['展现', '点击', '消费', '对话', '转出', '有效']].apply(lambda x: x.sum())
    hz_plan = hz_plan.fillna('0')
    return render_template('data.html',
                           now=int(time.time()),
                           baidu_account=[baidu_account.to_html(classes='data')],
                           baidu_plan=[baidu_plan.to_html(classes='data')],
                           sogou_account=[sogou_account.to_html(classes='data')],
                           sogou_plan=[sogou_plan.to_html(classes='data')],
                           shenma_account=[shenma_account.to_html(classes='data')],
                           shenma_plan=[shenma_plan.to_html(classes='data')],
                           d360_account=[d360_account.to_html(classes='data')],
                           d360_plan=[d360_plan.to_html(classes='data')],
                           dhz_account=[hz_account.to_html(classes='data')],
                           dhz_plan=[hz_plan.to_html(classes='data')]
                           )
@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500







