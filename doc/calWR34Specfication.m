%%
function calWR34Specfication(fname,cf,bw)

S2p=LoadS2p( path); 
fre=S2p(:,1);%频率
S21=S2p(:,3);
Lam=20*log10(abs(S21));
fl=S2p(1,1); fu=S2p(end,1); step=S2p(2,1)-S2p(1,1);
fbu0=cf+bw/2; fbl0=cf-bw/2;
idxu0=round((fbu0-fl)/step+1);
idxl0=round((fbl0-fl)/step+1);

Lamav(iter,jter)=10*log10(sum(abs((S21(idxl0:idxu0))).^2)/(idxu0-idxl0+1));%平均值
Lrip(iter,jter)=max(Lam(idxl0:idxu0))-min(Lam(idxl0:idxu0));%S21范围内部最大最小值的差
LripR(iter,jter)=max(diff(Lam(idxl0:idxu0))./step*1e6);%S21导数最大值
RL(iter,jter)=max(20*log10(abs(S2p(idxl0:idxu0,5))));%S22最大值
CPRL(iter,jter)=max(20*log10(abs(S2p(idxl0:idxu0,2))));%S11最大值
GD=-diff(angle(S21(idxl0:idxu0)))./diff(fre(idxl0:idxu0))/2/pi*1e9;%s21相位导数,群时延
for kter=2:length(GD)-1 %平滑群时延
            if abs(GD(kter))>abs((GD(kter-1)+GD(kter+1))*10)
                     GD(kter)=(GD(kter-1)+GD(kter+1))/2;
            end
end
GD=smooth(GD);
GDrip(iter,jter)=max(GD)-min(GD);
GDripR(iter,jter)=max(diff(GD)./step*1e6);

end
%%
function S=LoadS2p(path)

    fid=fopen(path);
    A=fread(fid,'*char');
    A=A.';
    len=length(A);
    idx1=strfind(A, '#');
    idx2=strfind(A, '!');
    tmp=max([idx1 idx2]);
    idx3=strfind(A(tmp:tmp+100), 10 );
    tmp=idx3(1)+tmp;
    tmp1=['[' strtrim(A(tmp:len)) ']'];
    SS=str2num(tmp1);
    for iter=1:length(idx2)
        if idx2(iter)>idx1
            tmp=idx2(iter);
            break
        end
    end
    Scmt=upper(A(idx1+1:tmp-1));
    [fre_unit,remainStr]=strtok(Scmt,' ');
    switch char(fre_unit)
        case 'GHZ'
            S(:,1)=SS(:,1)*1e9;
        case 'MHZ'
            S(:,1)=SS(:,1)*1e6;
        case 'KHZ'   
            S(:,1)=SS(:,1)*1e3;
        case 'HZ'
            S(:,1)=SS(:,1);
    end
    [~,remainStr]=strtok(remainStr,' ');
    [S_fmt,tmp]=strtok(remainStr,' ');
    if isempty(tmp)
        S_fmt=S_fmt(1:2);
    end
    switch char(S_fmt)
        case 'RI'
                    S(:,2)=SS(:,2)+1i*SS(:,3);
                    S(:,3)=SS(:,4)+1i*SS(:,5);
                    S(:,4)=SS(:,6)+1i*SS(:,7);
                    S(:,5)=SS(:,8)+1i*SS(:,9);
        case 'MA'
                    S(:,2)=SS(:,2).*exp(1i*SS(:,3)/180*pi);
                    S(:,3)=SS(:,4).*exp(1i*SS(:,5)/180*pi);
                    S(:,4)=SS(:,6).*exp(1i*SS(:,7)/180*pi);
                    S(:,5)=SS(:,8).*exp(1i*SS(:,9)/180*pi);
        case 'DB'
                    S(:,2)=10.^(SS(:,2)/20).*exp(1i*SS(:,3)/180*pi);
                    S(:,3)=10.^(SS(:,4)/20).*exp(1i*SS(:,5)/180*pi);
                    S(:,4)=10.^(SS(:,6)/20).*exp(1i*SS(:,7)/180*pi);
                    S(:,5)=10.^(SS(:,8)/20).*exp(1i*SS(:,9)/180*pi);
    end
    fclose(fid);
end