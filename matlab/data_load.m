function [ ecg, r ] = data_load( index )
%DATA_LOAD 此处显示有关此函数的摘要
%   此处显示详细说明
ecg = load(['../dat/icbeb2019/data/data_',num2str(index, '%05d'),'.mat']);
ecg = ecg.ecg;
R_peak = load(['../dat/icbeb2019/ref/R_',num2str(index, '%05d'),'.mat']);
r = R_peak.R_peak;
end

