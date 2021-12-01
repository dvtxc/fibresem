%Note: This is the endpoint for the "togglefig" function and the start of
%the "showMaskAsOverlay" function. Recommendation is to copy and save both
%of these files in a seperate .m file for increased code speed. 

function varargout = showMaskAsOverlay(opacity, mask, overlaycolor, varargin)
error(nargchk(1,5,nargin));
if nargin >= 4
    if ~isempty(varargin{1})
        if ishandle(varargin{1})
            imgax = varargin{1};
        else
            figure;
            imshow(varargin{1});
            imgax = imgca;
        end
    else
        imgax = imgca;
    end
    fig = get(imgax,'parent');
    axes(imgax);
else
    fig = gcf;
end

if nargin == 5
    deleMasks = logical(varargin{2});
else
    deleMasks = true;
end

iptcheckinput(opacity, {'double'},{'scalar'}, mfilename, 'opacity', 1);
iptcheckinput(deleMasks, {'logical'}, {'nonempty'}, mfilename, 'deleMasks', 5);

if nargin == 1
    overlay = findall(gcf,'tag','opaqueOverlay');
    if isempty(overlay)
        error('SHOWMASKASOVERLAY: No opaque mask found in current figure.');
    end
    mask = get(overlay,'cdata');
    newmask = max(0,min(1,double(any(mask,3))*opacity));
    set(overlay,'alphadata',newmask);
    figure(fig);
    return
else
    iptcheckinput(mask, {'double','logical'},{'nonempty'}, mfilename, 'mask', 2);
end

DEFAULT_COLOR = [1 0 0];
if nargin < 3
    overlaycolor = DEFAULT_COLOR;
elseif ischar(overlaycolor)
    switch overlaycolor
        case {'y','yellow'}
            overlaycolor = [1 1 0];
        case {'m','magenta'}
            overlaycolor = [1 0 1];
        case {'c','cyan'}
            overlaycolor = [0 1 1];
        case {'r','red'}
            overlaycolor = [1 0 0];
        case {'g','green'}
            overlaycolor = [0 1 0];
        case {'b','blue'}
            overlaycolor = [0 0 1];
        case {'w','white'}
            overlaycolor = [1 1 1];
        case {'k','black'}
            overlaycolor = [0 0 0];
        otherwise
            disp('Unrecognized color specifier; using default.');
            overlaycolor = DEFAULT_COLOR;
    end
end

figure(fig);
tmp = imhandles(fig);
if isempty(tmp)
    error('There doesn''t appear to be an image in the current figure.');
end
try
    a = imattributes(tmp(1));
catch %#ok
    error('There doesn''t appear to be an image in the current figure.');
end
imsz = [str2num(a{2,2}),str2num(a{1,2})]; 

if ~isequal(imsz,size(mask(:,:,1)))
    error('Size mismatch');
end
if deleMasks
    delete(findall(fig,'tag','opaqueOverlay'))
end

overlaycolor = im2double(overlaycolor);
mask = logical(mask);

if size(mask,3) == 1
    newmaskR = zeros(imsz);
    newmaskG = newmaskR;
    newmaskB = newmaskR;
    newmaskR(mask) = overlaycolor(1);
    newmaskG(mask) = overlaycolor(2);
    newmaskB(mask) = overlaycolor(3);
elseif size(mask,3) == 3
    newmaskR = mask(:,:,1);
    newmaskG = mask(:,:,2);
    newmaskB = mask(:,:,3);
else
    beep;
    disp('Unsupported masktype in showImageAsOverlay.');
    return
end
newmask = cat(3,newmaskR,newmaskG,newmaskB);
hold on;
h = imshow(newmask);
try
    set(h,'alphadata',double(mask)*opacity,'tag','opaqueOverlay');
catch %#ok
    set(h,'alphadata',opacity,'tag','opaqueOverlay');
end
if nargout > 0
    varargout{1} = imhandles(imgca);
end
if nargout > 1
    varargout{2} = getframe;
    varargout{2} = varargout{2}.cdata;
end
end 