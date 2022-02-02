%Note: It is recommended to move the "togglefig" and "showMaskAsOverlay" functions to seperate .m
%files in the same folder as the main Matlab Code. Save the file as "togglefig.m" and "showMaskAsOverlay.m" respectively. 
%Alternatively, download the togglefig and showMaskASOverlay functions online. 
%This will increase the Matlab method speed significantly. 
                   
function fig = togglefig(name, clearfig)
if ~nargin
    tmp = get(findall(0,'type','figure'),'name');
    if isempty(tmp)
        tmp = 0;
    elseif ischar(tmp)
        tmp = 1;
    else 
        tmp = sum(cell2mat(regexp(tmp,'untitled')));
    end
    name = ['untitled',num2str(tmp+1)];
    clearfig = 0;
elseif nargin == 1
    clearfig = 0;
end

fig = findall(0,'type','figure','name',name);
if isempty(fig)
    fig = figure('numbertitle','off','name',name);shg;
else
    set(0,'currentfigure',fig)
end
drawnow;
figure(fig)
if clearfig
    clf
end
if ~nargout
    clear fig
end
end