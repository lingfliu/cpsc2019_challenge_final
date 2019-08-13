clear; clc;

data_pulse = [98,173,223,224,245,813,814,815,822,833,841,949,950];
data_glitch = [125,126,167,176,177,183,184,188,198,199,200,...
    232,233,244,246,341,342,401,527,528,529,550,565,569,...
    624,647,648,649,650,651,736,753,815,870,893,894,895,...
    896,897,928,998,1020,1052,1160,1248,1277,1278,1313,...
    1314,1316,1362,1405,1406,1412,1433,1439,1445,1550,...
    1564,1580,1588,1589,1596,1600,1613,1643,1649,1650,...
    1651,1652,1666,1671,1676,1678,1704,1708,1753,1755,1794,...
    1795,1807,1815,1817,1834,1835,1842,1863,1864,1865,1871,1886,1912];
for idx = 1:length(data_glitch)    
    [ecg, r] = data_load(data_glitch(idx));          
% for idx = 1:2000
%     [ecg, r] = data_load(idx);          
    ecg = med_filter(ecg, 3);
    
    med10 = med_filter(ecg, 30);
    med20 = med_filter(ecg, 40);
    med30 = med_filter(ecg, 50);
%     med100 = med_filter(ecg, 100);
    med50 = med_filter(ecg, 75);
    
    med = mean([med10, med20, med30, med50], 2);
    
    subplot(1,2,1)
%     ecg_med50 = med_filter(ecg, 20);
%     plot(ecg_med50, 'lineWidth', 3.0)
%     plot(diff(ecg))        
%     ecg = baseline_med(ecg, 150);
    plot(ecg, 'lineWidth',2.0);
    hold on
    plot(med, 'lineWidth', 3.0);
    
    
    
    ecg_med = ecg-med;
    plot((ecg_med-mean(ecg_med))/std(ecg_med)-5, 'lineWidth',3.0)
    hold off

    med = med20;
    subplot(1,2,2)
    plot(ecg, 'lineWidth',2.0);
    hold on
    hold on
    plot(med, 'lineWidth', 3.0);
    ecg_med = ecg-med;
    plot((ecg_med-mean(ecg_med))/std(ecg_med)-5, 'lineWidth',3.0)
    
%     ecg30= baseline_med(ecg, 50);
%     plot((ecg30-mean(ecg30))/std(ecg30), 'lineWidth',3.0)
%         hold on
%     ecg20 = baseline_med(ecg, 30);
%     ecg20 = ecg;
%     plot((ecg20-mean(ecg20))/std(ecg20), 'lineWidth',3.0)

    stem(r, ones(length(r)), 'r')
    legend('med30', 'ecg','r')
%     title(data_glitch(idx))
    title(idx)
    hold off
    pause
end