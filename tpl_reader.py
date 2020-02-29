import os
import pandas as pd
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import sys
import warnings
warnings.filterwarnings("ignore")   # suppress warnings in notebook output

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)

minimum_start_point = 1000


class Tpl:
    """
    Data extraction for tpl files (OLGA >= 6.0)
    """

    def __init__(self, fname):
        """
        Initialize the tpl attributes
        """
        if fname.endswith(".tpl") is False:
            raise ValueError("not a tpl file")
        self.fname = fname.split(os.sep)[-1]
        self.path = os.sep.join(fname.split(os.sep)[:-1])
        if self.path == '':
            self.abspath = self.fname
        else:
            self.abspath = self.path + os.sep + self.fname
        self._attributes = {}
        self.data = {}
        self.label = {}
        self.trends = {}
        self.time = ""
        with open(self.abspath) as fobj:
            for idx, line in enumerate(fobj):
                if 'CATALOG' in line:
                    self._attributes['CATALOG'] = idx
                    self._attributes['nvars'] = idx + 1
                if 'TIME SERIES' in line:
                    self._attributes['data_idx'] = idx
                    break
                if 'CATALOG' in self._attributes:
                    adj_idx = idx - self._attributes['CATALOG'] - 1
                    if adj_idx > 0:
                        self.trends[adj_idx] = line

    def filter_data(self, pattern=''):
        """
        Filter available variables
        """
        filtered_trends = {}
        with open(self.abspath) as fobj:
            for idx, line in enumerate(fobj):
                variable_idx = idx - self._attributes['CATALOG'] - 1
                if 'TIME SERIES' in line:
                    break
                if pattern in line and variable_idx > 0:
                    filtered_trends[variable_idx] = line
        return filtered_trends

    def extract(self, variable_idx):
        """
        Extract a specific variable
        """
        self.time = np.loadtxt(self.abspath,
                               skiprows=self._attributes['data_idx'] + 1,
                               unpack=True, usecols=(0,))
        data = np.loadtxt(self.abspath,
                          skiprows=self._attributes['data_idx'] + 1,
                          unpack=True,
                          usecols=(variable_idx,))
        with open(self.abspath) as fobj:
            for idx, line in enumerate(fobj):
                if idx == 1 + variable_idx + self._attributes['CATALOG']:
                    try:
                        self.data[variable_idx] = data[:len(self.time)]
                    except TypeError:
                        self.data[variable_idx] = data.base
                    self.label[variable_idx] = line.replace("\'",
                                                            '').replace("\n",
                                                                        "")
                    break

    def to_excel(self, *args):
        """
        Dump all the data to excel, fname and path can be passed as args
        """
        path = os.getcwd()
        fname = self.fname.replace(".tpl", "_tpl") + ".xlsx"
        idxs = self.filter_data("")
        for idx in idxs:
            self.extract(idx)
        data_df = pd.DataFrame(self.data)
        data_df.columns = self.label.values()
        data_df.insert(0, "Time [s]", self.time)
        if len(args) > 0 and args[0] != "":
            path = args[0]
            if os.path.exists(path) == False:
                os.mkdir(path)
            data_df.to_excel(path + os.sep + fname)
        else:
            data_df.to_excel(self.path + os.sep + fname)


class TplFile(Tpl):
    """
    read and parse one tpl file
    """

    def __init__(self, filename):
        super().__init__(filename)
        self.data_all = 0
        self.data_trends = pd.DataFrame()
        self.data_trends_summary = 0
        self.q_liq_m3day = 0
        self.wc = 0
        self.gor = 0
        self.p_atm = 0
        self.d_mm = 0
        # self.PI = 0
        # self.p_res_atm = 0
        # self.p_wh_atm = 0
        # self.d_choke_mm = 0

        self.file_name = filename
        self.tpl_split = re.compile(r'\'*\s*\'', re.IGNORECASE)
        self.df = pd.DataFrame()
        self.df_super = pd.DataFrame()
        params = self.filter_data('POSITION:')  # get all trends with POSITION:

        for i in params:
            params.update({i: self.tpl_split.split(params[i])})

        self.fd = pd.DataFrame(params, index=['key', 'sect', 'position', 'dim', 'msg', '2']).T
        self.position_list = self.fd['position'].unique()
        self.key_list = self.fd['key'].unique()  # список ключевых слов

        self.extract_all()

    def extract_all(self):
        """
        extract all columns to DataFrame
        """
        self.data_all = np.loadtxt(self.abspath,
                                   skiprows=self._attributes['data_idx'] + 1,
                                   unpack=True)
        """put in in DataFrame for further manipulations"""
        self.df = pd.DataFrame(self.data_all).T
        dic = {}
        dic.update({0: 'time'})
        for v in self.trends:
            dic.update({v: self.trends[v].replace("'", " ")})

        self.df.columns = dic.values()
        self.df.index = self.df.time.round(0)

    def get_trend(self, key_list, pipe_list):
        """
        method to extract trends for some pipe and set of keys
        :param key_list:
        :param pipe_list:
        :return:
        """

        self.data_trends = pd.DataFrame(index=self.df.index)
        for pipe in pipe_list:
            for key in key_list:
                key1 = key + ":" + pipe
                if not self.df.filter(like=key + " ").filter(like=pipe + " ").empty:
                    self.data_trends[key1] = self.df.filter(like=key + " ").filter(like=pipe + " ").values
        global minimum_start_point
        self.data_trends = self.data_trends[minimum_start_point:]
        return self.data_trends

    def get_trend_summary(self):
        """calculate summary data on trends extracted"""
        global minimum_start_point
        self.data_trends_summary = pd.DataFrame()
        self.data_trends_summary['mean'] = self.df_super[minimum_start_point:].mean()
        self.data_trends_summary['min'] = self.df_super[minimum_start_point:].min()
        self.data_trends_summary['max'] = self.df_super[minimum_start_point:].max()
        self.data_trends_summary['key'] = self.df_super.columns.str.split(pat=':').str[0]
        self.data_trends_summary['point'] = self.df_super.columns.str.split(":").str[1]

        self.data_trends_summary['q_liq'] = self.q_liq_m3day
        self.data_trends_summary['wc'] = self.wc
        self.data_trends_summary['gor'] = self.gor
        self.data_trends_summary['press'] = self.p_atm
        self.data_trends_summary['diam'] = self.d_mm

        return self.data_trends_summary

    def get_trends_super(self, position_list):
        """
        method extractor trends for specific keys and add calculated fields to it
        """
        # keys = ['USL', 'USG', 'QT', 'QLST', 'QGST']
        keys = ['PT', 'TM', 'HOL', 'ROF', 'YVOL', 'HOLWT', 'USG', 'USLT', 'USLTWT', 'ACCOIQ', 'ACCLIQ']
        self.df_super = pd.DataFrame()
        for point in position_list:
            df = self.get_trend(keys, [point])
            # print(df)
            # df['SLUGVEL:'+point] = (df['USFEXP:'+point]+df['USTEXP:'+point])*0.5
            # dft = df['HOLEXP:'+point]- df['HOLEXP:'+point].mean()
            # dft[dft<0] = 0
            # df['SLUGHL:'+point]=dft
            # df['MECH:'+point] = force_fraction(vel_ms=df['SLUGVEL:'+point],
            #                                   rho_kgm3=800 * df['SLUGHL:'+point])
            self.df_super = pd.concat([self.df_super, df], axis=1)
        return self.df_super


class TplParams:
    """
    class read all data from parametric study
    and allows to manipulate it
    """

    def __init__(self, pathname):
        """
        set path
        read files
        estimate parameters variation
        """
        self.tpl_path = pathname
        self.file_name_mask = '*.tpl'
        self.files = glob(self.tpl_path + self.file_name_mask)
        print(len(self.files), 'файла найдено.')
        self.count_files = 0  # number of cases loaded
        self.file_num = 0
        self.file_list = {}

        self.qliq_list = []
        self.wc_list = []
        self.gor_list = []
        self.p_list = []
        self.d_list = []
        # self.PI_list = []
        # self.p_res_list = []
        # self.p_wh_list = []
        # self.d_choke_list = []

        # self.choke_list = []
        # self.PI_list = []
        self.df = pd.DataFrame()
        self.df_super = pd.DataFrame()
        self.key_list = ['PT', 'TM', 'HOL', 'ROF', 'YVOL', 'HOLWT', 'USG', 'USLT', 'USLTWT', 'ACCOIQ', 'ACCLIQ']
        # self.pipe_list = []
        self.position_list = []
        self.flSplit = re.compile(r'[-,;]', re.IGNORECASE)
        self.num_table = pd.DataFrame()
        self.name = ''
        self.key_list_all = []
        # """
        # параметры трубы
        # """
        # self.ID_mm = 800  # внутренний диамет трубы
        # self.dens_liq_kgm3 = 800  # плотность жидкости
        # self.weight_kgm = 200  # удельный вес трубы

    def read_data(self):
        """
        read all files
        tries to get params from file names
        :return:
        """
        self.num_table = pd.DataFrame(columns=['num', 'q_liq', 'wc', 'gor', 'press', 'diam'])
        self.file_num = 0
        count = 0
        for file in self.files:  # iterating through all files
            # try:
            par = self.flSplit.split(file)
            par[-1] = par[-1][:-4]
            fl_read = TplFile(file)  # read file
            fl_read.q_liq_m3day = float(par[1])
            fl_read.wc = float(par[3])
            fl_read.gor = float(par[5])
            fl_read.p_atm = float(par[7])
            fl_read.d_mm = float(par[9])

            fl_read.get_trends_super(fl_read.position_list)
            fl_read.get_trend_summary()
            self.file_list.update({self.file_num: fl_read})  # put reader object to dictionary

            self.num_table.loc[self.file_num] = [self.file_num, fl_read.q_liq_m3day, fl_read.wc, fl_read.gor,
                                                 fl_read.p_atm, fl_read.d_mm]
            self.file_num = self.file_num + 1

            count += 1
            sys.stdout.write("\r" + str(count) + " .tpl моделей прочитано.")
            sys.stdout.flush()

        df_list = []
        for df in self.file_list.values():
            df_list.append(df.data_trends_summary)
        self.df = pd.concat(df_list)
        # self.pipe_list = fl_read.pipe_list
        self.position_list = fl_read.position_list
        self.key_list_all = fl_read.key_list
        self.qliq_list = self.df['q_liq'].unique()
        self.wc_list = self.df['wc'].unique()
        self.gor_list = self.df['gor'].unique()
        self.p_list = self.df['press'].unique()
        self.d_list = self.df['diam'].unique()

        # self.PI_list = self.df['PI'].unique()
        # self.p_res_list = self.df['p_res'].unique()
        # self.p_wh_list = self.df['p_wh'].unique()
        # self.d_choke_list = self.df['d_choke'].unique()
        print('\nread done.')

    def calc_data(self):
        """
        recalculate main DataFrame into table with
        row - some point (file) with point, q_liq, q_gas, p and slug_vel mech_factor params
        :return:
        """
        # agr_type = ['mean', 'min', 'max']
        self.df_super = pd.pivot_table(self.df,
                                       values=['mean', 'max', 'min'],
                                       index=['point', 'q_liq', 'wc', 'gor', 'press', 'diam'],
                                       columns=['key'])
        self.df_super = self.df_super.reset_index()
        """
        calc additional data needed to calculate all params
        """

        self.df_super['slug_holdup'] = self.df_super['max', 'HOL']
        self.df_super['slug_vel_liq'] = - self.df_super['min', 'USLT']
        self.df_super['slug_vel_gas'] = - self.df_super['min', 'USG']
        self.df_super['water_holdup'] = self.df_super['max', 'HOLWT']
        self.df_super['slug_vel_water'] = - self.df_super['min', 'USLTWT']
        self.df_super['height'] = self.df_super['mean', 'YVOL']
        self.df_super['max_pt'] = self.df_super['max', 'PT'] / 101325
        self.df_super['rof'] = self.df_super['max', 'ROF']
        self.df_super['max_acql'] = self.df_super['max', 'ACCLIQ']
        self.df_super['max_acqo'] = self.df_super['max', 'ACCOIQ']

        print('calc done.')

    def get_matr_ql_qg(self, position=0, wc=0, press=0, diam=0, val='max_pt'):

        """
        convert data read to some format
        :param position:
        :param wc:
        :param press:
        :param diam:
        :param val:
        :return:
        """

        if type(position) == int:
            position = self.position_list[position]
        if wc == 0:
            wc = self.wc_list[0]
        if press == 0:
            press = self.p_list[0]
        if diam == 0:
            diam = self.d_list[0]

        df1 = pd.pivot_table(self.df_super,
                             index=['point', 'q_liq', 'wc', 'press', 'diam'],
                             columns=['gor'],
                             values=val)
        df1.columns = df1.columns.droplevel(0)
        df1 = df1.reset_index()
        df1.index = df1.q_liq
        df1 = df1[df1.point == position]
        df1 = df1[df1.wc == wc]
        df1 = df1[df1.press == press]
        df1 = df1[df1.diam == diam]
        df1 = df1.drop(['point', 'q_liq', 'wc', 'press', 'diam'], 1)
        df1 = df1.sort_index(ascending=False)

        df2 = pd.pivot_table(self.df_super, index=['point'],  values=val, aggfunc=np.max)

        df2 = df2.reset_index()
        df2 = df2[df2.point == position]
        i = 0 + df2[val]
        return df1, i

    def get_number_tpl(self, q_liq_list, wc_list, gor_list, p_list, d_list):
        nt = self.num_table
        out = nt[(nt.q_liq.isin(q_liq_list)) &
                 (nt.wc.isin(wc_list)) &
                 (nt.gor.isin(gor_list)) &
                 (nt.press.isin(p_list)) &
                 (nt.diam.isin(d_list))]['num'].values
        return out

    def get_trend(self, key_list, point_list, q_liq_list, wc_list, gor_list, p_list, d_list): #, PI_list, p_res_list, p_wh_list, d_choke_list):
        n = self.get_number_tpl(q_liq_list, wc_list, gor_list, p_list, d_list)
        out = pd.DataFrame()
        for file_num in n:
            a = self.file_list[file_num].get_trend(key_list, point_list)
            colname_list_new = []
            for colname in a.columns:
                colname_list_new.append(colname
                                        + ' :q_liq ' + str(self.file_list[file_num].q_liq_m3day)
                                        + ' :wc ' + str(self.file_list[file_num].wc)
                                        + ' :gor ' + str(self.file_list[file_num].gor)
                                        + ' :press ' + str(self.file_list[file_num].p_atm)
                                        + ' :diam ' + str(self.file_list[file_num].d_mm))
            a.columns = colname_list_new
            out = pd.concat([out, a], axis=1)
        if key_list == ['PT']:
            return out/101325
        else:
            return out

