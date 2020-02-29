
"""

Ppl class

"""

import os

import re
import sys
import pandas as pd
from glob import glob
import numpy as np
 

class Ppl:

    """
    Data extraction for ppl files (OLGA >= 6.0)
    """
    def __init__(self, fname):
        """
        Initialize the ppl attributes
        """
        if fname.endswith(".ppl") is False:
            raise ValueError("not a ppl file")

        self.fname = fname.split(os.sep)[-1]
        self.path = os.sep.join(fname.split(os.sep)[:-1])
        if self.path == '':
            self.abspath = self.fname
        else:
            self.abspath = self.path+os.sep+self.fname
        self._attributes = {}
        self._attributes['branch_idx'] = []
        self.data = {}
        self.label = {}
        self.profiles = {}
        self.geometries = {}
        self.key_words = []
        with open(self.abspath) as fobj:
            for idx, line in enumerate(fobj):
                if 'CATALOG' in line:
                    self._attributes['CATALOG'] = idx
                    nvar_idx = idx+1
                if 'TIME SERIES' in line:
                    self._attributes['data_idx'] = idx
                    break
                if 'CATALOG' in self._attributes:
                    adj_idx = idx-self._attributes['CATALOG']-1
                    if adj_idx > 0:
                        self.profiles[adj_idx] = line
                        # print(adj_idx, line)
                if 'BRANCH\n' in line:
                    self._attributes['branch_idx'].append(idx+1)

        with open(self.abspath) as fobj:
            self._attributes['nvar'] = int(fobj.readlines()[nvar_idx])
        self._time_series()
        with open(self.abspath) as fobj:
            text = fobj.readlines()
        for branch_idx in self._attributes['branch_idx']:
            branch_raw = text[branch_idx]
            branch = branch_raw.replace("\'", '').replace("\n", '')
            self.extract_geometry(branch, branch_idx+2)


    def _time_series(self):
        with open(self.abspath) as fobj:
            self.time = []
            for line in fobj.readlines()[1+self._attributes['data_idx']::
                                         self._attributes['nvar']+1]:
                self.time.append(float(line))



    def filter_data(self, pattern=''):
        """
        Filter available varaibles
        """
        filtered_profiles = {}
        with open(self.abspath) as fobj:
            for idx, line in enumerate(fobj):
                if 'TIME SERIES' in line:
                    break
                if pattern in line and (idx-self._attributes['CATALOG']-1) > 0:
                    filtered_profiles[idx-self._attributes['CATALOG']-1] = line
        return filtered_profiles

    def _define_branch(self, variable_idx):
        return re.findall(r"'[\w\ \:\-]*'", \
                          self.profiles[variable_idx])[2].replace("'", "")

    def extract_geometry(self, branch, branch_begin):
        """
        It adds to self.geometries a specific geometry as (x, y)
        """
        raw_geometry = []
        with open(self.abspath) as fobj:
            for line in fobj.readlines()[branch_begin:]:
                points = []
                for point in line.split(' '):
                    try:
                        points.append(float(point))
                    except ValueError:
                        pass
                raw_geometry.extend(points)
                if 'CATALOG' in line or 'BRANCH' in line:
                    break
        xy_geo = raw_geometry
        self.geometries[branch] = (xy_geo[:int(len(xy_geo)/2)],
                                   xy_geo[int(len(xy_geo)/2):])

    def extract(self, variable_idx):
        """
        Extract a specific varaible
        """
        branch = self._define_branch(variable_idx)
        # print(branch)
        label = self.profiles[variable_idx].replace("\n", "")
        # print(label)
        self.label[variable_idx] = label
        self.data[variable_idx] = [[], []]
        with open(self.abspath) as fobj:
            for line in fobj.readlines()[variable_idx+1+self._attributes['data_idx']::self._attributes['nvar']+1]:
                points = []
                for point in line.split(' '):
                    try:
                        points.append(float(point))
                    except ValueError:
                        pass
                # print(points)
                self.data[variable_idx][1].append(np.array(points))
        x_st = self.geometries[branch][0]
        # print(x_st)
        x_no_st = [(x0+x1)/2 for x0, x1 in zip(x_st[:-1], x_st[1:])]
        # print(x_no_st)
        if len(self.data[variable_idx][1][0]) == len(x_st):
            self.data[variable_idx][0] = np.array(x_st)
        else:
            self.data[variable_idx][0] = np.array(x_no_st)
        # print(self.data[variable_idx])

    def to_excel(self, *args):
        """
        Dump all the data to excel, fname and path can be passed as args

        """

        path = os.getcwd()
        fname = self.fname.replace(".ppl", "_ppl") + ".xlsx"
        if len(args) > 0 and args[0] != "":
            path = args[0]
            if os.path.exists(path) == False:
                os.mkdir(path)
        xl_file = pd.ExcelWriter(path + os.sep + fname)
        for idx in self.filter_data(""):
            self.extract(idx)
        labels = list(self.filter_data("").values())
        for prof in self.data:
            data_df = pd.DataFrame()
            data_df["X"] = self.data[prof][0]
            for timestep, data in zip(self.time, self.data[prof][1]):
                data_df[timestep] = data
            myvar = labels[prof-1].split(" ")[0]
            br_label = labels[prof-1].split("\'")[5]
            unit = labels[prof-1].split("\'")[7].replace("/", "-")
            mylabel = "{} - {} - {}".format(myvar, br_label, unit)
            data_df.to_excel(xl_file, sheet_name=mylabel)
        xl_file.save()


class PplFile(Ppl):
    """
    read and parse one ppl file
    same way as TplFile class 
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
        self.annul = 0
        self.d_choke_mm = 0

        self.file_name = filename
        self.ppl_split = re.compile(r'\'*\s*\'', re.IGNORECASE)
        self.df = pd.DataFrame()
        self.df_super = pd.DataFrame()
        params = self.filter_data()  # get all trends with PIPELINE:

        for i in params:
            params.update({i: self.ppl_split.split(params[i])})

        self.fd = pd.DataFrame(params, index=['key', 'type', 'branch', 'pipe', 'dim','msg', 'garbage']).T
        self.pipe_list = self.fd['pipe'].unique()
        self.key_list = self.fd['key'].unique()  # список ключевых слов

        self.extract_all()

    def extract_all(self):
        """
        extract all columns to DataFrame dictionary
        :return: 
        """
        """sequntially extract all vectors one by one"""
        for i in self.fd.index:
            super().extract(i)
        """
        self.dftp will be dictionary of dictionary of profile dataframes
        first key - pipe name
        second key - timestep number
        """
        self.dftp={}
        pipe_done=[]
        self.time_steps = len(self.data[1][1])
        for pipe1 in self.pipe_list:
            for i in self.data.keys():
                if self.fd['pipe'][i] == pipe1 and pipe1 not in pipe_done:
                    gstep = self.data[i][0]
                    tdic={}
                    for j in range(0, self.time_steps):
                        """create new dataframe in dict"""
                        tdic.update({j: pd.DataFrame(index=gstep)})
                    self.dftp.update({pipe1: tdic})
                    pipe_done.append(pipe1)
                    
            
        """ loop by keys """
        for i in self.data.keys():
            #tstep = self.data[i][1]
            """ loop by time steps """
            for j in range(0,self.time_steps):
                """there are two type of values - boundary and section
                    we must differentiate it here 
                    we just add last value to section type values - 
                    to make it same size as boundary
                    it can be not good - we shift sections values from 
                    middle of section to its edge    rnt"""
                if self.fd['type'][i]=='BOUNDARY:':
                    newcol = self.data[i][1][j]
                if self.fd['type'][i]=='SECTION:':
                    newcol = np.append(self.data[i][1][j],self.data[i][1][j][-1])
                #    newcol = 0
                new_key = self.fd['key'][i]
                pp = self.fd['pipe'][i]
                #print(new_key, len(newcol))
                self.dftp[pp][j][new_key] = newcol
            
    def get_trend(self, key_list,  time_point_list=[0], pipe_list=[], shift=0):
        """
        method to extract trends for all pipes and set of keys
        """
        resl = []
        for tt in time_point_list:
            ldf = {}
            mlist = {}
            if len(pipe_list) == 0:
                pipe_list = self.pipe_list
            for pp in self.pipe_list:
                minl = self.dftp[pp][tt].index.min() + shift
                maxl = self.dftp[pp][tt].index.max() - shift
                df = self.dftp[pp][tt].loc[minl:maxl, key_list]
                if len(pipe_list) > 0:
                    mlist.update({pp: df.index.max()})
                ldf.update({pp: df})
            m=0
            for i in range(0,len(pipe_list)):
                if i>0:
                    m = m + mlist[pipe_list[i-1]]
                ldf[pipe_list[i]].index = ldf[pipe_list[i]].index + m
                
            resdf = pd.concat(ldf.values())
            resdf.sort_index(inplace=True)
            resdf = resdf.groupby(resdf.index).mean()
            resl.append(resdf)
        return resl


def get_all_ppl(path):

    file_name_mask = '*.ppl'
    files = glob(path + file_name_mask)
    print(len(files), '.ppl файла найдено.')
    # print(files)
    ppl_dict = {}
    flSPlit = re.compile(r'[-,;]', re.IGNORECASE)
    count = 0

    for file in files:
        par = flSPlit.split(file)
        par[0] = par[0].split("\\")[-1]
        par[-1] = par[-1][:-4]
        # name = (i for i in par)
        name = ('Qliq', float(par[1]), 'WC', float(par[3]), 'GOR', float(par[5]), 'Pressure', float(par[7]), 'diameter', float(par[9]))
        ppl_dict[name] = Ppl(file)

        count += 1
        sys.stdout.write("\r" + str(count) + " .ppl моделей прочитано.")
        sys.stdout.flush()

    print("\r" + str(count) + " .ppl моделей прочитано.")
    return(ppl_dict)
    
    
