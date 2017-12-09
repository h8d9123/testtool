
function MeaAna2WHZ()
%% 改一下存放路径===========================


chidx=[2 4 6 8 7 5 3 1];
[~,pidx]=sort(chidx);
  



Path_Results='.\WR34.txt';

path0='.\WR34NewFlt\20\28G_J';
path1='.\WR34NewFlt\25\28G_J';
path2='.\WR34NewFlt\60\28G_J';



Rjav1=zeros(1,8);Rjav2=zeros(1,8);
f0=[27725       27975       28225       28475       28725       28975       29625       29875]*1e6;
BW0=230e6;
BW1=216e6;
%%
%====================================
fid = fopen(Path_Results, 'w');
for iter=1:8%channel
    
    for jter=1:3
       if jter==1
                pathx=path0;
                t='.';
            elseif  jter==2
                pathx=path1;
                 t='-';
            elseif  jter==3
                pathx=path2;
                 t='--';
       end
    path=[pathx,num2str(pidx(iter)), '.s2p'];
    % path=[path0,num2str((iter)), '.s2p'];
    S2p=LoadS2p( path);
    fre=S2p(:,1);
    S21=S2p(:,3);
    Lam=20*log10(abs(S21));

    fl=S2p(1,1);fu=S2p(end,1);step=S2p(2,1)-S2p(1,1);
    fbu0=f0(iter)+BW0/2;fbl0=f0(iter)-BW0/2;
    idxu0=round((fbu0-fl)/step+1);
    idxl0=round((fbl0-fl)/step+1);
    Lamav(iter,jter)=10*log10(sum(abs((S21(idxl0:idxu0))).^2)/(idxu0-idxl0+1));
    Lrip(iter,jter)=max(Lam(idxl0:idxu0))-min(Lam(idxl0:idxu0));
    LripR(iter,jter)=max(diff(Lam(idxl0:idxu0))./step*1e6);
    RL(iter,jter)=max(20*log10(abs(S2p(idxl0:idxu0,5))));
    CPRL(iter,jter)=max(20*log10(abs(S2p(idxl0:idxu0,2))));
    GD=-diff(angle(S21(idxl0:idxu0)))./diff(fre(idxl0:idxu0))/2/pi*1e9;

        for kter=1:length(GD)-1
        if kter==1
            if abs(GD(kter))>abs(GD(kter+1)*10)
                    GD(kter)=GD(kter+1);
            end

        else
            if abs(GD(kter))>abs((GD(kter-1)+GD(kter+1))*10)
                     GD(kter)=(GD(kter-1)+GD(kter+1))/2;
            end
        end
        end

    GD=smooth(GD);
    figure(3)
    plot(fre(idxl0:idxu0-1)/1e9,GD,t)
    hold on
    % 
    % if max(GD)>100
    %     [~,idx]=max(GD);
    %     GD(idx)=[];
    %     GDrip(iter)=max(GD)-min(GD);
    % else
        GDrip(iter,jter)=max(GD)-min(GD);
       GDripR(iter,jter)=max(diff(GD)./step*1e6);

    fbu01=f0(iter)+BW1/2;fbl01=f0(iter)-BW1/2;
    idxu01=round((fbu01-fbl0)/step+1);
    idxl01=round((fbl01-fbl0)/step+1);   
    GD1=GD(idxl01:idxu01);
     GDrip1(iter,jter)=max(GD1)-min(GD1);    
    GDripR1(iter,jter)=max(diff(GD1)./step*1e6);

    grid on
     xlabel('Frequency (GHz)','fontsize',20,'fontweight','b')
    ylabel('Group Delay (ns)','fontsize',20,'fontweight','b')
    axis([27.5 30.1 8 20])

    if iter~=1
    fbu01=f0(iter-1)+BW0/2;
    fbl01=f0(iter-1)-BW0/2;
    idxu01=round((fbu01-fl)/step+1);
    idxl01=round((fbl01-fl)/step+1);
    Rjav1(iter,jter)=10*log10(sum(abs((S21(idxl01:idxu01))).^2)/(idxu01-idxl01+1));
    end
    if iter~=8
    fbu02=f0(iter+1)+BW0/2;
    fbl02=f0(iter+1)-BW0/2;
    idxu02=round((fbu02-fl)/step+1);
    idxl02=round((fbl02-fl)/step+1);
    Rjav2(iter,jter)=10*log10(sum(abs((S21(idxl02:idxu02))).^2)/(idxu02-idxl02+1));
    end
    if iter==1
        Rjav(iter,jter)=Rjav2(iter,jter)-Lamav(iter,jter);
    elseif iter==8
        Rjav(iter,jter)=Rjav1(iter,jter)-Lamav(iter,jter);
    else
        Rjav(iter,jter)=(Rjav1(iter,jter)+Rjav2(iter,jter))/2-Lamav(iter,jter);
    end


    figure(1)
    plot(S2p(:,1)/1e9,20*log10(abs(S2p(:,3))),t,S2p(:,1)/1e9,20*log10(abs(S2p(:,4))),t,S2p(:,1)/1e9,20*log10(abs(S2p(:,2))),t);
     axis([27.5 30.1 -40 0])
    xlabel('Frequency (GHz)','fontsize',20,'fontweight','b')
    ylabel('S Parameter (dB)','fontsize',20,'fontweight','b')
     hold on
     grid on
    figure(2)
    plot(S2p(:,1)/1e9,20*log10(abs(S2p(:,5))),t)
     axis([27.5 30.1 -30 0])
     hold on
     grid on
     xlabel('Frequency (GHz)','fontsize',20,'fontweight','b')
    ylabel('S Parameter (dB)','fontsize',20,'fontweight','b')
                 
    end
    
   fprintf(fid, '%5.2f  %5.2f  %5.2f \n',Lamav(iter,:));
   fprintf(fid, '%5.2f  %5.2f  %5.2f  \n',max(Lamav(iter,:))-min(Lamav(iter,:)),0,0);
   fprintf(fid, '%5.2f  %5.2f  %5.2f \n',Lrip(iter,:));
   fprintf(fid, '%5.2f  %5.2f  %5.2f \n',LripR(iter,:));
   fprintf(fid, '%5.2f  %5.2f  %5.2f \n',GDrip(iter,:)); 
    fprintf(fid, '%5.2f  %5.2f  %5.2f \n',GDripR(iter,:));
   fprintf(fid, '%5.2f  %5.2f  %5.2f \n',GDrip1(iter,:)); 
    fprintf(fid, '%5.2f  %5.2f  %5.2f \n',GDripR1(iter,:));
    fprintf(fid, '%5.2f  %5.2f  %5.2f \n',Rjav(iter,:));
    fprintf(fid, '%5.2f  %5.2f  %5.2f \n',RL(iter,:));
    fprintf(fid, '%5.2f  %5.2f  %5.2f \n',CPRL(iter,:));
%      fprintf(fid,'======================================================= \n') 
end



fclose(fid);
end








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