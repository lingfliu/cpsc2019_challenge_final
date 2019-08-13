import wfdb
from wfdb import processing
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from sig_tool import resample
import shutil
import os
from sig_tool import interpolate

from concurr_tool import MultiTask
def detect_qrs(sig, fs):
    # qrs_idx = processing.xqrs_detect(sig, fs) # using xqrs algorithm
    qrs_idx = processing.qrs.gqrs_detect(sig, fs) # using gqrs algorithm
    return qrs_idx

"""
format annotations
"""
def format_anno(wfdb_data, wfdb_label):
    return None

def _gen_default_dbdir():
    return os.path.join(os.getcwd(), 'wfdb')

def dl_all_db(db_dir=None):
    if not db_dir:
        db_dir = _gen_default_dbdir()

    dbs = wfdb.get_dbs()
    for db in dbs:
        db_name = db[0]
        print('downloading db: ', db[0], ' ', db[1])
        wfdb.dl_database(db_name+'/', dl_dir=os.path.join(db_dir, db_name))


def dl_dbs(dbs, db_dir=None):
    if not db_dir:
        db_dir = _gen_default_dbdir()

    for db in dbs:
        wfdb.dl_database(db+'/', dl_dir=os.path.join(db_dir, db))


def load_database(database, db_dir):

    dir = os.path.join(db_dir, database)

    file_list = []
    for root, dirs, files in os.walk(dir):
        [file_list.append(f) for f in files]

    dat_list = [a.split('.')[0] for a in filter(lambda x:x.split('.')[1]=='dat', file_list)]
    hea_list = [a.split('.')[0] for a in filter(lambda x:x.split('.')[1]=='hea', file_list)]
    atr_list = [a.split('.')[0] for a in filter(lambda x:x.split('.')[1]=='atr', file_list)]

    record_list = [dat for dat in filter(lambda x:x in hea_list and x in atr_list, dat_list)]

    name_list = []
    data_list = []
    anno_list = []
    anno_typ_list = []
    for rec in record_list:
        print('loading data', rec)
        data = wfdb.rdrecord(os.path.join(dir, rec))
        anno = wfdb.rdann(os.path.join(dir, rec), 'atr')

        sig = data.p_signal
        anno_idx = np.zeros(len(sig))
        anno_typ_idx = np.ones(len(sig))*(-1)
        for idx in range(len(anno.sample)):
            anno_idx[anno.sample[idx]] = 1
            anno_typ_idx[anno.sample[idx]] = anno.subtype[idx]

        data_list.append(sig)
        anno_list.append(anno_idx)
        anno_typ_list.append(anno_typ_idx)
        name_list.append(rec)

        # plt.plot(sig)
        # plt.plot(anno_idx)
        # plt.show()


    return name_list, data_list, anno_list, anno_typ_list


def is_beat(anno_symb):
    beat_anno = ['N', 'L', 'R', 'B', 'A', 'a', 'J', 'S', 'V', 'r', 'F', 'e', 'j', 'n', 'E', '/', 'f', 'Q', '?']
    nobeat_anno = ['[', '!', ']', 'x', '(', ')', 'p', 't', 'u', '`', '\'', '^', '|', '~', '+', 's', 'T', '*', 'D', '=', '\"', '@']
    if anno_symb in beat_anno:
        return True
    else:
        return False

def load_mitdb(set_len=5000, db_dir='wfdb', database='mitdb'):
    (name_list, data_list, anno_list, anno_typ_list) = load_database(database, db_dir)

    ''' resample before splitting'''
    print('start resampling')
    cnt = 0

    # draw_idx = 23
    # plt.figure()
    # plt.plot(data_list[draw_idx])
    # plt.plot(anno_list[draw_idx])
    # plt.show()
    # s = resample(data_list[draw_idx], 360, 500, 'linear')
    # anno = resample(anno_list[draw_idx], 360, 500, 'label')
    # plt.figure()
    # plt.plot(s)
    # plt.plot(anno)
    # plt.show()

    multiTask = MultiTask(pool_size=40, queue_size=5000)
    for d in data_list:
        multiTask.submit(cnt, resample, (d, 360, 500, 'linear'))
        cnt += 1
    rs_data = [d for d in multiTask.subscribe()]

    cnt = 0
    multiTask = MultiTask(pool_size=40, queue_size=5000)
    for a in anno_list:
        multiTask.submit(cnt, resample, (a, 360, 500, 'label'))
        cnt += 1
    rs_anno = [a for a in multiTask.subscribe()]

    cnt = 0
    multiTask = MultiTask(pool_size=40, queue_size=5000)
    for a in anno_typ_list:
        multiTask.submit(cnt, resample, (a, 360, 500, 'label_str'))
        cnt += 1
    rs_anno_typ = [a for a in multiTask.subscribe()]


    return name_list, rs_data, rs_anno, rs_anno_typ


def load_aha(db_dir='wfdb', database='aha'):

    dir = os.path.join(db_dir, database)
    file_list = []
    for root, dirs, files in os.walk(dir):
        [file_list.append(f) for f in files]

    dat_list = [a.split('.')[0] for a in filter(lambda x:x.split('.')[1] == 'dat', file_list)]
    hea_list = [a.split('.')[0] for a in filter(lambda x:x.split('.')[1] == 'hea', file_list)]
    atr_list = [a.split('.')[0] for a in filter(lambda x:x.split('.')[1] == 'atr', file_list)]

    record_list = [dat for dat in filter(lambda x:x in hea_list and x in atr_list, dat_list)]

    name_list = []
    data_list = []
    anno_list = []
    anno_typ_list = []

    # cnt = 0
    for rec in record_list:
        # cnt += 1
        # if cnt > 10:
        #     break
        print('loading data', rec)
        data = wfdb.rdrecord(os.path.join(dir, rec))
        anno = wfdb.rdann(os.path.join(dir, rec), 'atr')

        sig = data.p_signal
        '''aha: local peaks to trace the R peak'''

        '''test code to check nan in data'''
        # has_nan = False
        # for idx in range(len(sig)):
        #     if np.isnan(sig[idx,0]) or np.isnan(sig[idx,1]):
        #         has_nan = True
        #         print(idx)
        # if has_nan:
        #     plt.title(rec)
        #     plt.plot(sig[:,0])
        #     plt.plot(sig[:,1]-2)
        #     plt.show()

        '''nan handling by interpolation'''
        # idx_start = -1
        # idx_stop = -1
        # for idx in range(len(sig)):
        #     if np.isnan(sig[idx,0]):
        #         if idx_start < 0:
        #             idx_start = idx - 1
        #     else:
        #         if idx_start >= 0:
        #             idx_stop = idx
        #
        #     if idx_start >= 0 and idx_stop >= 0:
        #         print('ch0 interpolating from ', idx_start, ' to ', idx_stop)
        #         sig_interp = interpolate(sig[idx_start,0], sig[idx_stop,0], idx_stop-idx_start+1)
        #         cnt = 0
        #         for idx in range(len(sig_interp)):
        #             sig[idx_start+idx,0] = sig_interp[idx]
        #         idx_start = -1
        #         idx_stop = -1
        #
        # idx_start = -1
        # idx_stop = -1
        # for idx in range(len(sig)):
        #     if np.isnan(sig[idx,1]):
        #         if idx_start < 0:
        #             idx_start = idx - 1
        #     else:
        #         if idx_start >= 0:
        #             idx_stop = idx
        #
        #     if idx_start >= 0 and idx_stop >= 0:
        #         print('ch1 interpolating from ', idx_start, ' to ', idx_stop)
        #         sig_interp = interpolate(sig[idx_start,1], sig[idx_stop,1], idx_stop-idx_start+1)
        #         cnt = 0
        #         for idx in range(len(sig_interp)):
        #             sig[idx_start+idx,1] = sig_interp[idx]
        #
        #         idx_start = -1
        #         idx_stop = -1

        peaks = processing.find_local_peaks(sig[:,0], 10)

        idx2 = 0
        anno_r = []
        for idx in anno.sample:
            idx_start = idx2
            for idx_peak in peaks[idx_start:]:
                idx2 += 1
                '''aha: find the nearest R peak after the QRS onset'''
                if idx_peak > idx:
                    anno_r.append(idx_peak)
                    break

        anno_r_idx = np.zeros(len(sig[:,0]))
        for idx in anno_r:
            anno_r_idx[idx] = 1
        anno_typ = anno.subtype
        anno_typ_idx = [''] * len(sig)
        for idx in range(len(anno_r)):
            anno_typ_idx[anno_r[idx]] = anno_typ[idx]

        # trunc the data
        sig = sig[anno_r[0]-200:]
        anno_r_idx = anno_r_idx[anno_r[0]-200:]
        anno_r = anno_r - (anno_r[0] + 200)
        anno_typ_idx = anno_typ_idx[anno_r[0]-200:]

        data_list.append(sig)
        anno_list.append(anno_r_idx)
        anno_typ_list.append(anno_typ_idx)

        name_list.append(rec)

        for idx in range(len(sig)):
            if any(np.isnan(sig[idx])):
                print(rec, 'nan ', idx)
                break

    ''' resample before splitting'''
    print('start resampling')
    cnt = 0
    multiTask = MultiTask(pool_size=40, queue_size=5000)
    for d in data_list:
        multiTask.submit(cnt, resample, (d, 250, 500, 'linear'))
        cnt += 1
    rs_data = [d for d in multiTask.subscribe()]

    cnt = 0
    multiTask = MultiTask(pool_size=40, queue_size=5000)
    for a in anno_list:
        multiTask.submit(cnt, resample, (a, 250, 500, 'label'))
        cnt += 1
    rs_anno = [a for a in multiTask.subscribe()]

    cnt = 0
    multiTask = MultiTask(pool_size=40, queue_size=5000)
    for a in anno_typ_list:
        multiTask.submit(cnt, resample, (a, 250, 500, 'label_str'))
        cnt += 1
    rs_anno_typ = [a for a in multiTask.subscribe()]


    return name_list, rs_data, rs_anno, rs_anno_typ
