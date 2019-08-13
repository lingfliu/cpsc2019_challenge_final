function [ sig_med ] = med_filter( sig, med_len )
%MED_FILTER 此处显示有关此函数的摘要
%   此处显示详细说明
sig_med = zeros(size(sig));
for m = 1:length(sig)
    if m <= med_len
        sig_med(m) = median(sig(1:m+med_len));
    elseif m > length(sig)-med_len
        sig_med(m) = median(sig(m-med_len:end));
    else
        sig_med(m) = median(sig(m-med_len:m+med_len));
    end
end
end

