# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 15:30:27 2019

@author: Rinat Khabibullin
"""

import itertools  
# import New_tpl_reader as tp
# import New_ppl_reader as pl
import seaborn as sns
# import numpy as np
# import pandas as pd
import matplotlib.pyplot as plt

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
# select a palette
from bokeh.palettes import Category10 as palette


def plot_trend_two(pln,
                   crv,
                   key=['PT'],
                   pos=['POS-1'],
                   title='title',
                   xlab='',
                   ylab='',
                   p1leg='прямолинейная траектория',
                   c1leg='искривленная траектория',
                   multx=1,
                   multy=1):
    """
    функция для отрисовки графиков трендов для двух объектов TplFile
    изначально предназначена для сравнения двух кейсов - плоского и изогнутого

    :param pln: первый объект с трендами OLGA (плоский)
    :param crv: второй объект с трендами OLGA (искривленный)
    :param key: список ключей которые будут отрисованы
    :param pos: список позиций для которых будут отрисованы тренды
    :param title: общий заголовок графика
    :param xlab: подпись по оси x
    :param ylab: подпись по оси y
    :param p1leg: подпись легенды для первого объекта (основа)
    :param c1leg: подпись легенды для второго объекта (основа)
    :param multx: множитель для оси x
    :param multy: множитель для оси y
    :return: рисует bokeh plot
    """

    """  prepare plot """
    p1 = pln.get_trend(key, pos)*multy
    c1 = crv.get_trend(key, pos)*multy
    ttl = title
    for ps in pos:
        ttl = ttl+':'+ps
    p = figure( 
               plot_width=900,
               plot_height=400,
               title=ttl,
               x_axis_label=xlab,
               y_axis_label=ylab)
    """  create a color iterator """
    colors = itertools.cycle(palette[10])  
    for clname in p1.columns:
        p.line(p1.index*multx, p1[clname], color=next(colors), legend=p1leg+':'+clname)
    for clname in c1.columns:
        p.line(c1.index*multx, c1[clname], color=next(colors), legend=c1leg+':'+clname)
    p.legend.location = "bottom_right"
    p.legend.click_policy = "hide"
    show(p)

def plot_trend_one(pln,
                   key=['PT'],
                   pos=['POS-1'],
                   title='title',
                   xlab='',
                   ylab='',
                   p1leg='прямолинейная траектория',
                   multx=1,
                   multy=1):
    """
    функция для отрисовки графиков трендов для двух объектов TplFile
    изначально предназначена для сравнения двух кейсов - плоского и изогнутого

    :param pln: первый объект с трендами OLGA (плоский)
    :param key: список ключей которые будут отрисованы
    :param pos: список позиций для которых будут отрисованы тренды
    :param title: общий заголовок графика
    :param xlab: подпись по оси x
    :param ylab: подпись по оси y
    :param p1leg: подпись легенды для первого объекта (основа)
    :param c1leg: подпись легенды для второго объекта (основа)
    :param multx: множитель для оси x
    :param multy: множитель для оси y
    :return: рисует bokeh plot
    """

    """  prepare plot """
    p1 = pln.get_trend(key, pos)*multy
    ttl = title
    for ps in pos:
        ttl = ttl+':'+ps
    p = figure(
               plot_width=900,
               plot_height=400,
               title=ttl,
               x_axis_label=xlab,
               y_axis_label=ylab)
    """  create a color iterator """
    colors = itertools.cycle(palette[10])
    for clname in p1.columns:
        p.line(p1.index*multx, p1[clname], color=next(colors), legend=p1leg+':'+clname)
    p.legend.location = "bottom_right"
    p.legend.click_policy = "hide"
    show(p)
    
def plot_prof_two(pln,
                  crv,
                  key=['PT'],
                  title='title',
                  xlab='',
                  ylab='',
                  multy=1,
                  pipe_list=[],
                  time_list=[],
                  line=True,
                  shift=0):
    """
    функция для отрисовки графиков профилей для двух объектов PplFile
    изначально предназначена для сравнения двух кейсов - плоского и изогнутого

    :param pln: первый объект с трендами OLGA (плоский)
    :param crv: второй объект с трендами OLGA (искривленный)
    :param key: список ключей которые будут отрисованы
    :param title: общий заголовок графика
    :param xlab: подпись по оси x
    :param ylab: подпись по оси y
    :param multy: множитель для оси y
    :param pipe_list: список задающий последвательность труб для отрисовки
                последовательность важна - они будут стыковаться по заданному
                порядку
    :param time_list: список номеров моментов времени для отрисовки
                если не задать - отрисуются все моменты (не быстро)
    :param line: флаг показывает рисовать линии или точки
    :return:
    """
    
    # prepare plot
    ttl = title
    p = figure( 
               plot_width=900,
               plot_height=400,
               title=ttl,
               x_axis_label=xlab,
               y_axis_label=ylab)
    if len(time_list) == 0:
        time_list = range(0, pln.time_steps-1)
    for i in time_list:
        dfp = pln.get_trend(key, [i], pipe_list, shift=shift)[0] * multy
        dfp['time'] = dfp.index 
        dfc = crv.get_trend(key, [i], pipe_list, shift=shift)[0] * multy
        dfc['time'] = dfc.index 
        p1 = ColumnDataSource(dfp)
        c1 = ColumnDataSource(dfc)
        clr=0
        clr_list_pln=['orange', 'cyan']
        clr_list_crv=['red', 'blue']
        for k in key:
            if line:
                p.line(source=c1, x='time', y=k, color=clr_list_crv[clr], alpha=0.5)
                p.line(source=p1, x='time', y=k, color=clr_list_pln[clr], alpha=0.5)
            else:
                p.scatter(source=c1, x='time', y=k, color=clr_list_crv[clr], alpha=0.5)
                p.scatter(source=p1, x='time', y=k, color=clr_list_pln[clr], alpha=0.5)
            clr = clr+1
    show(p)


def plot_prof_one(pln,
                  key=['PT'],
                  title='title',
                  xlab='',
                  ylab='',
                  multy=1,
                  pipe_list=[],
                  time_list=[],
                  line=True,
                  shift=0):
    """
    функция для отрисовки графиков профилей для двух объектов PplFile
    изначально предназначена для сравнения двух кейсов - плоского и изогнутого

    :param pln: первый объект с трендами OLGA (плоский)
    :param crv: второй объект с трендами OLGA (искривленный)
    :param key: список ключей которые будут отрисованы
    :param title: общий заголовок графика
    :param xlab: подпись по оси x
    :param ylab: подпись по оси y
    :param multy: множитель для оси y
    :param pipe_list: список задающий последвательность труб для отрисовки
                последовательность важна - они будут стыковаться по заданному
                порядку
    :param time_list: список номеров моментов времени для отрисовки
                если не задать - отрисуются все моменты (не быстро)
    :param line: флаг показывает рисовать линии или точки
    :return:
    """

    # prepare plot
    ttl = title
    p = figure(
        plot_width=900,
        plot_height=400,
        title=ttl,
        x_axis_label=xlab,
        y_axis_label=ylab)
    if len(time_list) == 0:
        time_list = range(0, pln.time_steps - 1)
    for i in time_list:
        dfp = pln.get_trend(key, [i], pipe_list, shift=shift)[0] * multy
        dfp['time'] = dfp.index
        p1 = ColumnDataSource(dfp)
        clr = 0
        clr_list_pln = ['red', 'blue']
        for k in key:
            if line:
                p.line(source=p1, x='time', y=k, color=clr_list_pln[clr])
            else:
                p.scatter(source=p1, x='time', y=k, color=clr_list_pln[clr])
            clr = clr + 1
    show(p)

"""
==================================================================================
набор старых функций для рисования
==================================================================================
"""


def sublist(list_in, ind_list):
    list_out = []
    if type(ind_list) == int:
        list_out = list_in[ind_list]
    if type(ind_list) == list:
        list_out = [list_in[i] for i in ind_list]
    return list_out


def plot_trend(tpl, klist=['HOL'], position_num=0, q_liq_num=0, wc_num=0, gor_num=0, p_num=0, d_num=0):
    q_liq = sublist(tpl.qliq_list, q_liq_num)
    wc = sublist(tpl.wc_list, wc_num)
    gor = sublist(tpl.gor_list, gor_num)
    press = sublist(tpl.p_list, p_num)
    diam = sublist(tpl.d_list, d_num)
    position = sublist(tpl.position_list, position_num)
   # print(tpl.name, klist, position, 'q_liq  = ', q_liq, 'wc = ', wc, 'gor  = ', gor, 'press = ', press, 'diam  = ',
   #       diam)
    return tpl.get_trend(key_list=klist,
                         point_list=position,
                         q_liq_list=q_liq,
                         wc_list=wc,
                         gor_list=gor,
                         p_list=press,
                         d_list=diam)


def plot_trend_example(pl1, pl2, k, pos, ql, wc, gor, p, d):  # (pi, p_res, p_wh, d_choke)

    # AA = plt.figure(figsize=(17, 6), dpi=70)
    # AA.add_subplot(121)
    # plt.title(str(k[0]))
    d1 = plot_trend(pl1,
                    klist=[k[0]],
                    position_num=pos,
                    q_liq_num=ql,
                    wc_num=wc,
                    gor_num=gor,
                    p_num=p,
                    d_num=d)
    # AA.add_subplot(122)
    plt.title(str(k[0]))
    d2 = plot_trend(pl2,
                    klist=[k[0]],
                    position_num=pos,
                    q_liq_num=ql,
                    wc_num=wc,
                    gor_num=gor,
                    p_num=p,
                    d_num=d)

    plt.yticks(rotation="horizontal")
    # plt.ylim(min(min(d1.values) - 1, min(d2.values) - 1), max(max(d1.values) + 1, max(d2.values) + 1))
    plt.plot(d1, label="Plane")
    plt.plot(d2, label="Curved")
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_map(pl1, pl2, i, wc=0, p=0, d=0, val='PT', titl='', fmt='.2f'):
    a, vm_a = pl1.get_matr_ql_qg(position=pl1.position_list[i],
                                 wc=wc,
                                 press=p,
                                 diam=d,
                                 val=val)  # расчет карты по данным моделирования

    b, vm_b = pl2.get_matr_ql_qg(position=pl1.position_list[i],
                                 wc=wc,
                                 press=p,
                                 diam=d,
                                 val=val)  # расчет карты по данным моделирования

    AA = plt.figure(figsize=(17, 6), dpi=70)
    AA.add_subplot(121)
    plt.title('Карта для прямого трубопровода. ' + titl)
    sns.heatmap(a,
                annot=True,
                fmt=fmt,
                cmap="Reds",  # vmin=0, vmax=max(max(vm_a), max(vm_b)),
                linewidths=.5)  # построение визуального представления карты
    plt.yticks(rotation="horizontal")

    AA.add_subplot(122)
    plt.title('Карта для кривого трубопровода. ' + titl)
    sns.heatmap(b,
                annot=True,
                fmt=fmt,
                cmap="Reds",  # vmin=0, vmax=max(max(vm_a), max(vm_b)),
                linewidths=.5)  # построение визуального представления карты
    plt.yticks(rotation="horizontal")

    AA.show()
    plt.show()

    # Нахождение максимального элемента на карте плоского трубопровода
    a_max = a.max().max()  # максимальное значение
    a_i = a.max(axis=1).idxmax()  # дебит по жидкости
    a_j = a.max(axis=0).idxmax()  # дебит по газу
    a_i_idx = a.shape[0] - 1 - a.index.get_loc(a_i)  # индекс дебита по жидкости
    a_j_idx = a.columns.get_loc(a_j)  # индекс дебита по газу

    return a_max, a_i_idx, a_j_idx


def plot_map_delta_liq(tpl_plain, tpl_curved, ppl_plain, ppl_curved, i, i1=0, i2=0, wc=0, p=0, d=0, titl='', fmt='.2f'):
    word_dict = {'slug_holdup': 'HOL',
                 'slug_vel_liq': 'USLT',
                 'slug_vel_gas': 'USG',
                 'water_holdup': 'HOLWT',
                 'slug_vel_water': 'USLTWT'}

    val = 'slug_holdup'

    a, vm_a = tpl_plain.get_matr_ql_qg(position=tpl_plain.position_list[i],
                                       wc=wc,
                                       press=p,
                                       diam=d,
                                       val=val)  # расчет карты по данным моделирования

    b, vm_b = tpl_curved.get_matr_ql_qg(position=tpl_curved.position_list[i],
                                        wc=wc,
                                        press=p,
                                        diam=d,
                                        val=val)  # расчет карты по данным моделирования

    val = 'slug_holdup'
    for index in a.index:
        for row in a.columns:

            key = ('Qliq', index, 'WC', wc, 'GOR', row, 'Pressure', p, 'diameter', d)

            if key in ppl_plain.keys():
                file_plain = ppl_plain[key]
                file_curved = ppl_curved[key]

                keys_plain = file_plain.filter_data()

                number_to_extract = 0

                for key in keys_plain.keys():
                    # print("-" + keys_plain[key].split(r"'")[0][:-1] + "-", word_dict[val])
                    if keys_plain[key].split(r"'")[0][:-1] == word_dict[val]:
                        number_to_extract = int(key)

                file_plain.extract(number_to_extract)

                HOL_plain = file_plain.data[number_to_extract]
                HOL_plain = HOL_plain[1][int(round(len(HOL_plain) / 2, 0))]
                max_HOL_plain = max(HOL_plain[i1:i2])

                file_curved.extract(number_to_extract)
                HOL_curved = file_curved.data[number_to_extract]
                HOL_curved = HOL_curved[1][int(round(len(HOL_curved) / 2, 0))]
                max_HOL_curved = max(HOL_curved[i1:i2])

                a.loc[[index], [row]] = (max_HOL_curved - max_HOL_plain) / max_HOL_plain * 100

    """
    val = 'slug_vel_liq'
    for index in b.index:
        for row in b.columns:

            key = ('Qliq', index, 'WC', wc, 'GOR', row, 'Pressure', p, 'diameter', d)

            if key in ppl_plain.keys():
                file_plain = ppl_plain[key]
                file_curved = ppl_curved[key]

                keys_plain = file_plain.filter_data()

                number_to_extract = 0

                for key in keys_plain.keys():
                    # print("-" + keys_plain[key].split(r"'")[0][:-1] + "-", word_dict[val])
                    if keys_plain[key].split(r"'")[0][:-1] == word_dict[val]:
                        number_to_extract = int(key)

                file_plain.extract(number_to_extract)

                HOL_plain = file_plain.data[number_to_extract]
                HOL_plain = HOL_plain[1][int(round(len(HOL_plain) / 2, 0))]
                max_HOL_plain = max(HOL_plain[i1:i2])

                file_curved.extract(number_to_extract)
                HOL_curved = file_curved.data[number_to_extract]
                HOL_curved = HOL_curved[1][int(round(len(HOL_curved) / 2, 0))]
                max_HOL_curved = max(HOL_curved[i1:i2])

                b.loc[[index], [row]] = max_HOL_curved - max_HOL_plain
                """

    a.index.name = "Дебит жидкости, м3/сут"
    a.columns.name = "Газосодержание, м3/м3"

    b.index.name = "Дебит жидкости, м3/сут"
    b.columns.name = "Газосодержание, м3/м3"

    AA = plt.figure(figsize=(17, 6), dpi=70)

    # print('Карта для для плоского трубопровода')
    AA.add_subplot(121)
    plt.title("Образование жидкостной пробки")
    sns.heatmap(a, annot=True, fmt=fmt, cmap="YlOrBr",
                linewidths=.5)  # построение визуального представления карты

    plt.yticks(rotation="horizontal")

    """
    AA.add_subplot(122)
    plt.title("Торможение жидкости")
    sns.heatmap(b, annot=True, fmt=fmt, cmap="copper",
                linewidths=.5)  # построение визуального представления карты

    plt.yticks(rotation="horizontal")
    """

    AA.show()
    plt.show()


def plot_map_delta_GAS(tpl_plain, tpl_curved, ppl_plain, ppl_curved, i, i1=0, i2=0, wc=0, p=0, d=0, titl='', fmt='.2f'):
    word_dict = {'slug_holdup': 'HOL', 'slug_vel_liq': 'USLT', 'slug_vel_gas': 'USG', 'water_holdup': 'HOLWT',
                 'slug_vel_water': 'USLTWT'}

    val = 'slug_holdup'

    a, vm_a = tpl_plain.get_matr_ql_qg(position=tpl_plain.position_list[i], wc=wc, press=p, diam=d,
                                       val=val)  # расчет карты по данным моделирования

    b, vm_b = tpl_curved.get_matr_ql_qg(position=tpl_curved.position_list[i], wc=wc, press=p, diam=d,
                                        val=val)  # расчет карты по данным моделирования

    val = 'slug_holdup'
    for index in a.index:
        for row in a.columns:

            key = ('Qliq', index, 'WC', wc, 'GOR', row, 'Pressure', p, 'diameter', d)

            if key in ppl_plain.keys():
                file_plain = ppl_plain[key]
                file_curved = ppl_curved[key]

                keys_plain = file_plain.filter_data()

                number_to_extract = 0

                for key in keys_plain.keys():
                    # print("-" + keys_plain[key].split(r"'")[0][:-1] + "-", word_dict[val])
                    if keys_plain[key].split(r"'")[0][:-1] == word_dict[val]:
                        number_to_extract = int(key)

                file_plain.extract(number_to_extract)

                HOL_plain = file_plain.data[number_to_extract]
                HOL_plain = HOL_plain[1][int(round(len(HOL_plain) / 2, 0))]
                max_HOG_plain = max(1 - HOL_plain[i1:i2])

                file_curved.extract(number_to_extract)
                HOL_curved = file_curved.data[number_to_extract]
                HOL_curved = HOL_curved[1][int(round(len(HOL_curved) / 2, 0))]
                max_HOG_curved = max(1 - HOL_curved[i1:i2])

                a.loc[[index], [row]] = max_HOG_curved - max_HOG_plain

    val = 'slug_vel_gas'
    for index in b.index:
        for row in b.columns:

            key = ('Qliq', index, 'WC', wc, 'GOR', row, 'Pressure', p, 'diameter', d)

            if key in ppl_plain.keys():
                file_plain = ppl_plain[key]
                file_curved = ppl_curved[key]

                keys_plain = file_plain.filter_data()

                number_to_extract = 0

                for key in keys_plain.keys():
                    # print("-" + keys_plain[key].split(r"'")[0][:-1] + "-", word_dict[val])
                    if keys_plain[key].split(r"'")[0][:-1] == word_dict[val]:
                        number_to_extract = int(key)

                file_plain.extract(number_to_extract)

                HOL_plain = file_plain.data[number_to_extract]
                HOL_plain = HOL_plain[1][int(round(len(HOL_plain) / 2, 0))]
                max_HOL_plain = max(HOL_plain[i1:i2])

                file_curved.extract(number_to_extract)
                HOL_curved = file_curved.data[number_to_extract]
                HOL_curved = HOL_curved[1][int(round(len(HOL_curved) / 2, 0))]
                max_HOL_curved = max(HOL_curved[i1:i2])

                b.loc[[index], [row]] = max_HOL_curved - max_HOL_plain

    a.index.name = "Дебит жидкости, м3/сут"
    a.columns.name = "Газосодержание, м3/м3"

    b.index.name = "Дебит жидкости, м3/сут"
    b.columns.name = "Газосодержание, м3/м3"

    AA = plt.figure(figsize=(17, 6), dpi=70)

    # print('Карта для для плоского трубопровода')
    AA.add_subplot(121)
    plt.title("Образование газовой пробки")
    sns.heatmap(a, annot=True, fmt=fmt, cmap="Wistia",
                linewidths=.5)  # построение визуального представления карты

    plt.yticks(rotation="horizontal")

    AA.add_subplot(122)
    plt.title("Торможение газа")
    sns.heatmap(b, annot=True, fmt=fmt, cmap="afmhot",
                linewidths=.5)  # построение визуального представления карты

    plt.yticks(rotation="horizontal")

    AA.show()
    plt.show()


def plot_map_delta_WAT(tpl_plain, tpl_curved, ppl_plain, ppl_curved, i, i1=0, i2=0, wc=0, p=0, d=0, titl='', fmt='.2f'):
    word_dict = {'slug_holdup': 'HOL', 'slug_vel_liq': 'USLT', 'slug_vel_gas': 'USG', 'water_holdup': 'HOLWT',
                 'slug_vel_water': 'USLTWT'}

    val = 'slug_holdup'

    a, vm_a = tpl_plain.get_matr_ql_qg(position=tpl_plain.position_list[i], wc=wc, press=p, diam=d,
                                       val=val)  # расчет карты по данным моделирования

    b, vm_b = tpl_curved.get_matr_ql_qg(position=tpl_curved.position_list[i], wc=wc, press=p, diam=d,
                                        val=val)  # расчет карты по данным моделирования

    val = 'water_holdup'
    for index in a.index:
        for row in a.columns:

            key = ('Qliq', index, 'WC', wc, 'GOR', row, 'Pressure', p, 'diameter', d)

            if key in ppl_plain.keys():
                file_plain = ppl_plain[key]
                file_curved = ppl_curved[key]

                keys_plain = file_plain.filter_data()

                number_to_extract = 0

                for key in keys_plain.keys():
                    # print("-" + keys_plain[key].split(r"'")[0][:-1] + "-", word_dict[val])
                    if keys_plain[key].split(r"'")[0][:-1] == word_dict[val]:
                        number_to_extract = int(key)

                file_plain.extract(number_to_extract)

                HOL_plain = file_plain.data[number_to_extract]
                HOL_plain = HOL_plain[1][int(round(len(HOL_plain) / 2, 0))]
                max_HOL_plain = max(HOL_plain[i1:i2])

                file_curved.extract(number_to_extract)
                HOL_curved = file_curved.data[number_to_extract]
                HOL_curved = HOL_curved[1][int(round(len(HOL_curved) / 2, 0))]
                max_HOL_curved = max(HOL_curved[i1:i2])

                a.loc[[index], [row]] = max_HOL_curved - max_HOL_plain

    val = 'slug_vel_water'
    for index in a.index:
        for row in a.columns:

            key = ('Qliq', index, 'WC', wc, 'GOR', row, 'Pressure', p, 'diameter', d)

            if key in ppl_plain.keys():
                file_plain = ppl_plain[key]
                file_curved = ppl_curved[key]

                keys_plain = file_plain.filter_data()

                number_to_extract = 0

                for key in keys_plain.keys():
                    # print("-" + keys_plain[key].split(r"'")[0][:-1] + "-", word_dict[val])
                    if keys_plain[key].split(r"'")[0][:-1] == word_dict[val]:
                        number_to_extract = int(key)

                file_plain.extract(number_to_extract)

                HOL_plain = file_plain.data[number_to_extract]
                HOL_plain = HOL_plain[1][int(round(len(HOL_plain) / 2, 0))]
                max_HOL_plain = max(HOL_plain[i1:i2])

                file_curved.extract(number_to_extract)
                HOL_curved = file_curved.data[number_to_extract]
                HOL_curved = HOL_curved[1][int(round(len(HOL_curved) / 2, 0))]
                max_HOL_curved = max(HOL_curved[i1:i2])

                b.loc[[index], [row]] = max_HOL_curved - max_HOL_plain

    a.index.name = "Дебит нефти, м3/сут"
    a.columns.name = "Газосодержание, м3/м3"

    b.index.name = "Дебит нефти, м3/сут"
    b.columns.name = "Газосодержание, м3/м3"

    AA = plt.figure(figsize=(17, 6), dpi=70)

    # print('Карта для для плоского трубопровода')
    AA.add_subplot(121)
    plt.title("Образование водяной пробки")
    sns.heatmap(a, annot=True, fmt=fmt, cmap="winter",
                linewidths=.5)  # построение визуального представления карты

    plt.yticks(rotation="horizontal")

    AA.add_subplot(122)
    plt.title("Торможение воды")
    sns.heatmap(b, annot=True, fmt=fmt, cmap="bone",
                linewidths=.5)  # построение визуального представления карты

    plt.yticks(rotation="horizontal")

    AA.show()
    plt.show()


def plot_map_delta_press(pl1, pl2, i1, i2, wc=0, p=0, d=0, val='PT', titl='', fmt='.2f'):
    p_0, vm_a_0 = pl1.get_matr_ql_qg(position=pl1.position_list[i1], wc=wc, press=p, diam=d, val=val)
    p_1, vm_a_1 = pl1.get_matr_ql_qg(position=pl1.position_list[i2], wc=wc, press=p, diam=d, val=val)
    p_r_0, vm_b_0 = pl2.get_matr_ql_qg(position=pl1.position_list[i1], wc=wc, press=p, diam=d, val=val)
    p_r_1, vm_b_1 = pl2.get_matr_ql_qg(position=pl1.position_list[i2], wc=wc, press=p, diam=d, val=val)
    ro_0, vm_ro_0 = pl1.get_matr_ql_qg(position=pl1.position_list[i1], wc=wc, press=p, diam=d, val="rof")
    ro_1, vm_ro_1 = pl1.get_matr_ql_qg(position=pl1.position_list[i2], wc=wc, press=p, diam=d, val="rof")
    ro_r_0, vm_ro_0 = pl2.get_matr_ql_qg(position=pl1.position_list[i1], wc=wc, press=p, diam=d, val="rof")
    ro_r_1, vm_ro_1 = pl2.get_matr_ql_qg(position=pl1.position_list[i2], wc=wc, press=p, diam=d, val="rof")
    h_0, vm_ro_0 = pl1.get_matr_ql_qg(position=pl1.position_list[i1], wc=wc, press=p, diam=d, val="height")
    h_1, vm_ro_1 = pl1.get_matr_ql_qg(position=pl1.position_list[i2], wc=wc, press=p, diam=d, val="height")
    h_r_0, vm_ro_0 = pl2.get_matr_ql_qg(position=pl1.position_list[i1], wc=wc, press=p, diam=d, val="height")
    h_r_1, vm_ro_1 = pl2.get_matr_ql_qg(position=pl1.position_list[i2], wc=wc, press=p, diam=d, val="height")

    AA = plt.figure(figsize=(8, 6), dpi=70)


    AA.add_subplot(111)
    plt.title(titl)

    p_r = (p_r_1 + (ro_r_1 * 9.81) * h_r_1 / 101325) - (p_r_0 + (ro_r_0 * 9.81) * h_r_0 / 101325)
    p_p = (p_1 + (ro_1 * 9.81) * h_1 / 101325) - (p_0 + (ro_0 * 9.81) * h_0 / 101325)

    p_r.index.name = "Дебит нефти, м3/сут"
    p_r.columns.name = "Газовый фактор, м3/м3"

    p_p.index.name = "Дебит нефти, м3/сут"
    p_p.columns.name = "Газовый фактор, м3/м3"

    sns.heatmap(p_p - p_r, annot=True, fmt=fmt, cmap="YlGn",
                linewidths=.5)  # построение визуального представления карты
    plt.yticks(rotation="horizontal")

    AA.show()
    plt.show()


def plot_map_delta_accq(pl1, pl2, i1, i2, wc=0, p=0, d=0, val='max_acql', titl='', fmt='.2f'):
    ql_0, vm_a_0 = pl1.get_matr_ql_qg(position=pl1.position_list[i1], wc=wc, press=p, diam=d, val='max_acql')
    ql_1, vm_a_1 = pl2.get_matr_ql_qg(position=pl2.position_list[i2], wc=wc, press=p, diam=d, val='max_acql')

    qo_0, vm_a_0 = pl1.get_matr_ql_qg(position=pl1.position_list[i1], wc=wc, press=p, diam=d, val='max_acqo')
    qo_1, vm_a_1 = pl2.get_matr_ql_qg(position=pl2.position_list[i2], wc=wc, press=p, diam=d, val='max_acqo')

    AA = plt.figure(figsize=(17, 6), dpi=70)

    AA.add_subplot(121)
    plt.title(titl + " жидкости")
    ql = (ql_0 - ql_1)#/ql_1*100
    ql.index.name = "Дебит нефти, м3/сут"
    ql.columns.name = "Газовый фактор, м3/м3"
    sns.heatmap(ql, annot=True, fmt=fmt, cmap="Wistia", linewidths=.5)

    AA.add_subplot(122)
    plt.title(titl + " нефти")
    qo = (qo_0 - qo_1)#/qo_1*100
    qo.index.name = "Дебит нефти, м3/сут"
    qo.columns.name = "Газовый фактор, м3/м3"
    sns.heatmap(qo, annot=True, fmt=fmt, cmap="afmhot", linewidths=.5)

    plt.yticks(rotation="horizontal")

    AA.show()
    plt.show()
