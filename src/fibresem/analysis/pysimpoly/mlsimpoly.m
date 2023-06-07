I = imread(fullfile(pwd, 'output', '00-original-py.png'));
% take first channel
I = I(:,:,1);
pixelsize = 9.766;
pixelsizeunit = 'nm';

params.optimiseForThinFibres = true;
outputpath = fullfile(pwd, 'output');


%Enhance contract using histogram equalization
fprintf("Enhance contrast\n");

Ihist = adapthisteq(I);
saveimg(Ihist, '01-enhance-contrast');

Ihist = histeq(Ihist);
saveimg(Ihist, '02-enhance-contrast');


%Erode the grayscape image I and return the eroded image
fprintf("Erode Grayscale\n");
marker = imerode(Ihist, strel('disk', 5));
saveimg(marker, '03-erode');


%Perform morphological reconstruction of the image
fprintf("Morphological Reconstruction\n");
Iobr = imreconstruct(marker, Ihist);
saveimg(Iobr, '04-reconstruction');


%Find edges in intensity image
fprintf("Find edges\n");

min_area = 20;
E = edge(Iobr, 'Canny', [0.2 0.4]);
saveimg(E, '05-canny');


%Remove small objects with less than 20 pixels
E = bwareaopen(E, min_area);
saveimg(E, '06-areaopen');


E = bwmorph(E, 'thicken', 1);
saveimg(E, '07-thicken');

OL = imoverlay(Ihist, E, 'red');

%%

%Create a binary image from 2D grayscale by replacing all values above a
%globally determined threshold with 1s
fprintf("Create and optimise binary...\n");

level = graythresh(I) + 0.1;
saveimg(level, '08-graythresh');

BW = imbinarize(Ihist,level);
saveimg(BW, '09-imbinarize');

%Perform morphological closing on the image, returning the closed image.
BW = imclose(BW, strel('disk', 1));
saveimg(BW, '10-close');

%Apply a specific morphological operation to the binary image BW
BW = bwmorph(BW, 'clean', 100000);
BW = bwmorph(BW, 'fill', 5000);
BW = bwmorph(BW, 'majority', 500);
saveimg(BW, '11-clean-fill-majority');

if ~params.optimiseForThinFibres
    BW = bwmorph(BW, 'thin', 4);
end

%median filter than cleans image, stops when loop no longer changes image
fprintf("Cleaning: ");

BWf = medfilt2(BW);
i = 0;
while sum(sum(BWf)) ~= sum(sum(BW))
    i = i + 1;
    BW = BWf;
    BWf = medfilt2(BW);
    
    fprintf("#");
end

fprintf("\n");


%%
% Skeletonise
fprintf("Skeletonise\n");

if ~params.optimiseForThinFibres
    BW = bwmorph(BW, 'thicken', 4);
end

SK = bwskel(BW);

branchpoints = bwmorph(SK, 'branchpoints', 1);
branchpoints = imdilate(branchpoints, strel('disk', 3, 0));
SK = SK & ~branchpoints;
SK = bwmorph(SK, 'spur', 1);

% Uses edge overlay to filter out background noise
% To debug F, use imshow(F, []);
% If skeleton segment is at a large distance from edge: remove segment
fprintf("Clean skeleton:   0%%");

[m,n] = size(SK);
F=bwdist(E);
for i = 1:m
    for j = 1:n
        if SK(i,j)==1
            Ry=F(i,j);
            if Ry > 55
                SK(i,j) = 0;
            end
        end
    end
    fprintf("\b\b\b\b%3.0f%%", i/m * 100);
end

fprintf("\n");

togglefig('Segmented Image')
imshow(BW)
drawnow

%set(gca,'LooseInset',get(gca,'TightInset'));
imwrite(BW, fullfile(outputpath{1}, 'segmentation', outputpath{2}));
%close all

togglefig('Overlay')
OL = imoverlay(Ihist, SK, 'red');
imshow(OL)
showMaskAsOverlay(0.3, BW, 'c')

%set(gca,'LooseInset',get(gca,'TightInset'));
saveas(gcf, fullfile(outputpath{1}, 'overlay', outputpath{2}));
%close all
%%

%Calculate distance between a pixel and the nearest nonzero pixel;
%chessboard, cityblock, euclidean, quasi-euclidean
fprintf("Calculate diameters\n");

Dist = 2*bwdist(~BW);
diameters = Dist(SK);

fprintf("# Morphological Analysis Complete!\n");

togglefig('Data')
if conv > 0
    h = histogram(diameters*conv);
else
    h = histogram(diameters);
end
hold on
% findpeaks(h.Values, h.BinEdges(1:end-1), 'Threshold', 0.01*max(h.Values))
% [pks, loc] = findpeaks(h.Values, h.BinEdges(1:end-1), 'Threshold', 0.01*max(h.Values),'Annotate', 'peaks');
% [~,i] = max(pks);




y = [0 0 h.Values];
x = [h.BinEdges(1)-2 h.BinEdges(1)-1 h.BinEdges(1:end-1)];
f = fit(x',y','gauss1');

hold on
plot(f,x,y)
ylim([0 inf]);
ylabel('Frequency');
if conv > 0
    xlabel('Diameter (?m)');
    disp('Average Diameter (pixels)')
    ave = f.b1;
    avep = ave / conv;
    disp(avep)
    disp('Standard Deviation (pixels)')
    stdev = f.c1/2;
    stdevp = stdev / conv;
    disp(stdevp)
    disp('Average Diameter (?m)')
    disp(ave)
    disp('Standard Deviation (?m)')
    disp(stdev)
    dia_img = Dist.*SK * conv;
else
    xlabel('Diameter (pixels)');
    disp('Average Diameter (pixels)')
    ave = f.b1;
    disp(ave)
    disp('Standard Deviation (pixels)')
    stdev = f.c1/2;
    disp(stdev) 
    dia_img = Dist.*SK;
end

res = struct();
res.avg = ave;
res.sdev = stdev;
res.avgp = avep;
res.sdevp = stdevp;
res.diameters = diameters;

%set(gca,'LooseInset',get(gca,'TightInset'));
saveas(gcf, fullfile(outputpath{1}, 'histogram', outputpath{2}));
%close all

dia_img(dia_img == 0) = NaN;
%%
color = 0.05:0.05:0.95;
len = length(color);
RED = [1 0 0;
       ones(len,1) color' zeros(len,1)];
YELLOW = [1 1 0;
          flip(color)' ones(len,1) zeros(len,1)];
GREEN = [0 1 0];
     
%      flip(YELLOW);
%          flip(RED)]

map = [0 0 0;
       RED;
       YELLOW;
       GREEN];

togglefig('Diameter map')
imshow(dia_img);
colormap(map)
caxis([(ave - (3.35*stdev)), (ave + (3*stdev))])
colorbar('FontSize',14,'Ticks',[ave - (3*stdev), ave - (2*stdev), ave - stdev, ave,...
                  ave + stdev, ave + (2*stdev), ave + (3*stdev)],...
         'TickLabels',{'-3\sigma', '-2\sigma', '-1\sigma', 'Average',...
                       '+1\sigma', '+2\sigma', '+3\sigma'});  
                   
saveas(gcf, fullfile(outputpath{1}, 'diameter', outputpath{2}));
%% End of SIMPoly Matlab Method Code
                   
function saveimg(I, name)
    name = sprintf('%s-matlab.png', name);
    outputpath = fullfile(pwd, 'output', name);

    imwrite(I, outputpath);
    fprintf('Saved image %s\n', name);
end