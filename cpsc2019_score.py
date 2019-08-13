from CPSC2019_challenge import CPSC2019_challenge
import numpy as np
np.set_printoptions(threshold=np.inf)
import os
import re
from scipy import io

'''packages'''
from keras.models import load_model
from plain_data_make import PlainPreprocessor
from plain_model import hyper_params
from sig_tool import normalize, diff
import time
import pickle
from plain_model import  gen_pp_data_dir_name
import matplotlib.pyplot as plt

def load_ans(data_path_, rpos_path_, fs_):
    '''
    Please modify this function when you have to load model or any other parameters in CPSC2019_challenge()
    '''
    models = []

    # model = load_model('model_9705.h5')
    # models.append(model)
    #
    # model = load_model('model_9647.h5')
    # models.append(model)
    # model = load_model('model_9657.h5')
    # models.append(model)
    #
    # model = load_model('models/rematch_ckpt_plain_rev2_40_36874_0_044_0.0602_0.0994_0.9807_0.9670.h5') #conv-lstm
    # models.append(model)
    # model = load_model('models/rematch_ckpt_plain_rev2_40_36973_0_060_0.0676_0.1113_0.9789_0.9635.h5') #U-net FCN
    # models.append(model)
    # model = load_model('models/rematch_ckpt_plain_rev2_40_43632_0_347_0.0892_0.0877_0.9654_0.9665.h5') #lstm-conv
    # models.append(model)

    model = load_model('models/rematch_ckpt_plain_rev4_40_19031_0_031_0.0587_0.0711_0.9763_0.9722.h5')
    models.append(model)
    model = load_model('models/rematch_ckpt_plain_rev4_40_92098_0_047_0.0654_0.0733_0.9740_0.9720.h5')
    models.append(model)
    model = load_model('models/rematch_ckpt_plain_rev4_40_11085_0_037_0.0669_0.0644_0.9729_0.9741.h5')
    models.append(model)

    preprocessor = PlainPreprocessor(hyper_params)

    def is_mat(l):
        return l.endswith('.mat')
    ecg_files = list(filter(is_mat, os.listdir(data_path_)))
    rpos_files = list(filter(is_mat, os.listdir(rpos_path_)))
    HR_ref = []
    R_ref = []
    HR_ans = []
    R_ans = []
    cnt = 0
    for rpos_file in rpos_files:
        index = re.split('[_.]', rpos_file)[1]
        ecg_file = 'data_' + index + '.mat'

        ref_path = os.path.join(rpos_path_, rpos_file)
        ecg_path = os.path.join(data_path_, ecg_file)

        ecg_data = np.transpose(io.loadmat(ecg_path)['ecg'])[0]
        r_ref = io.loadmat(ref_path)['R_peak'].flatten()

        r_hr = np.array([loc for loc in r_ref if ((loc > 5.5 * fs_) and (loc < len(ecg_data) - 0.5 * fs_))])

        print('estimating ', ecg_path)
        ecg_data = preprocessor.single_preprocess(ecg_data)

        '''validate plotting'''
        # offset=0
        # data_dir = gen_pp_data_dir_name()
        # train_sig, pre_train_sig, pre_train_label = pickle.load(open(os.path.join(data_dir, 'icbeb_'+index +'.dat'), 'rb'))
        # sig = pre_train_sig[offset:offset+hyper_params['crop_len']]
        # sig_raw = sig
        # sig = normalize(sig)
        # sig = np.reshape(sig, newshape=(1,5000,1))
        # segs = []
        # for idx in range(3):
        #     seg = models[idx].predict(sig)
        #     segs.append(seg)
        # sig = normalize(sig_raw)
        # sig = diff(sig)
        # sig = np.reshape(sig, newshape=(1,5000,1))

        # for idx in range(3):
        #     seg = models[idx+3].predict(sig)
        #     segs.append(seg)
        #
        # seg = np.average(np.array(segs), axis=0)
        # seg = np.argmax(seg, axis=2)
        # plt.plot(sig[0])
        # plt.plot(ecg_data+0.5)
        # plt.plot(seg[0])
        # plt.plot(pre_train_label-0.5)
        # plt.legend(['pre', 'raw', 'seg', 'label'])
        # plt.show()

        hr_ans, r_ans = CPSC2019_challenge(ecg_data, models)
        r_ans = np.array(r_ans)
        print('finished ', ecg_path)

        HR_ref.append(round( 60 * fs_ / np.mean(np.diff(r_hr))))
        R_ref.append(r_ref)
        HR_ans.append(hr_ans)
        R_ans.append(r_ans)

    return R_ref, HR_ref, R_ans, HR_ans

def score(r_ref, hr_ref, r_ans, hr_ans, fs_, thr_):
    HR_score = 0
    record_flags = np.ones(len(r_ref))
    for i in range(len(r_ref)):
        FN = 0
        FP = 0
        TP = 0
        hr_der = abs(int(hr_ans[i]) - int(hr_ref[i]))
        if hr_der <= 0.02 * hr_ref[i]:
            HR_score = HR_score + 1
        elif hr_der <= 0.05 * hr_ref[i]:
            HR_score = HR_score + 0.75
        elif hr_der <= 0.1 * hr_ref[i]:
            HR_score = HR_score + 0.5
        elif hr_der <= 0.2 * hr_ref[i]:
            HR_score = HR_score + 0.25

        for j in range(len(r_ref[i])):
            loc = np.where(np.abs(r_ans[i] - r_ref[i][j]) <= thr_*fs_)[0]
            if j == 0:
                err = np.where((r_ans[i] >= 0.5*fs_) & (r_ans[i] <= r_ref[i][j] - thr_*fs_))[0]
            elif j == len(r_ref[i])-1:
                err = np.where((r_ans[i] >= r_ref[i][j]+thr_*fs_) & (r_ans[i] <= 9.5*fs_))[0]
            else:
                err = np.where((r_ans[i] >= r_ref[i][j]+thr_*fs_) & (r_ans[i] <= r_ref[i][j+1]-thr_*fs_))[0]

            FP = FP + len(err)
            if len(loc) >= 1:
                TP += 1
                FP = FP + len(loc) - 1
            elif len(loc) == 0:
                FN += 1

        if FN + FP > 1:
            record_flags[i] = 0
        elif FN == 1 and FP == 0:
            record_flags[i] = 0.3
        elif FN == 0 and FP == 1:
            record_flags[i] = 0.7

    rec_acc = round(np.sum(record_flags) / len(r_ref), 4)
    hr_acc = round(HR_score / len(r_ref), 4)

    print( 'QRS_acc: {}'.format(rec_acc))
    print('HR_acc: {}'.format(hr_acc))
    print('Scoring complete.')

    return rec_acc, hr_acc

if __name__ == '__main__':
    FS = 500
    THR = 0.075

    DATA_PATH = 'dat/icbeb2019/data'
    RPOS_PATH = 'dat/icbeb2019/ref/'

    R_ref, HR_ref, R_ans, HR_ans = load_ans(DATA_PATH, RPOS_PATH, FS)
    rec_acc, hr_acc = score(R_ref, HR_ref, R_ans, HR_ans, FS, THR)

    print('rec_acc:', rec_acc, 'hr_acc:', hr_acc)
