function res = simpoly(I, kwargs)
    %SIMPOLY Calculates fibre diameter distribution
    %   SIMPOLY calculates the fibre diamter distribution in a greyscale SEM
    %   image of electrospun fibres. The method is described in. ..
    %
    % INPUT:
    %
    % I               - input grayscale image
    % pixelsize       - pixel size in unit given by (pixelsizeunit) per pixel
    % pixelsizeunit   - pixel size unit
    % params          - struct containing additional parameters:
    %                   optimiseForThinFibres:  - optimise for fibres < 5 px.
    % outputpath      - path where output figures should be saved
    %
    % OUTPUT:
    %
    % res             - struct containing analysis results:
    %                   avg         - average in actual units
    %                   sdev        - standard deviation in actual units
    %                   avgp        - average in pixels
    %                   sdevp       - standard deviation in pixels
    %                   diameters   - all fibre diameters (in pixels)

    arguments
        I;
        kwargs.pixelsize = 1;
        kwargs.pixelsizeunit = 'px';
        kwargs.optimiseForThinFibres = true;
        kwargs.outputpath = fullfile(pwd, 'conversion-out');
    end

    fprintf("Received: %s\n", class(I));

    % Take first channel
    %I = I(:,:,1);

    pixelsize = kwargs.pixelsize;
    pixelsizeunit = kwargs.pixelsizeunit;
    outputpath = kwargs.outputpath;

    switch pixelsizeunit
        case 'mm'
            conv = pixelsize * 1000;
        case 'µm'
            conv = pixelsize;
        case 'nm'
            conv = pixelsize / 1000;
        otherwise
            conv = pixelsize;
    end

    %Enhance contract using histogram equalization
    fprintf("Enhance contrast\n");
    Ihist = adapthisteq(I);
    Ihist = histeq(Ihist);

    %Erode the grayscape image I and return the eroded image
    fprintf("Erode Grayscale\n");
    marker = imerode(Ihist, strel('disk', 5));

    %Perform morphological reconstruction of the image
    fprintf("Morphological Reconstruction\n");
    Iobr = imreconstruct(marker, Ihist);

    %Find edges in intensity image
    fprintf("Find edges\n");
    min_area = 20;
    E = edge(Iobr, 'Canny', [0.2 0.4]);

    %Remove small objects with less than 20 pixels
    E = bwareaopen(E, min_area);
    E = bwmorph(E, 'thicken', 1);

    OL = imoverlay(Ihist, E, 'red');

    %%

    %Create a binary image from 2D grayscale by replacing all values above a
    %globally determined threshold with 1s
    fprintf("Create and optimise binary...\n");
    level = graythresh(I) + 0.1;
    BW = imbinarize(Ihist,level);

    %Perform morphological closing on the image, returning the closed image.
    BW = imclose(BW, strel('disk', 1));

    %Apply a specific morphological operation to the binary image BW
    BW = bwmorph(BW, 'clean', 100000);
    BW = bwmorph(BW, 'fill', 5000);
    BW = bwmorph(BW, 'majority', 500);

    if ~kwargs.optimiseForThinFibres
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

    if ~kwargs.optimiseForThinFibres
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

    %togglefig('Segmented Image')
    %imshow(BW)
    %drawnow

    %%set(gca,'LooseInset',get(gca,'TightInset'));
    %imwrite(BW, fullfile(outputpath{1}, 'segmentation', outputpath{2}));
    %%close all

    %togglefig('Overlay')
    %OL = imoverlay(Ihist, SK, 'red');
    %imshow(OL)
    %showMaskAsOverlay(0.3, BW, 'c')

    %%set(gca,'LooseInset',get(gca,'TightInset'));
    %saveas(gcf, fullfile(outputpath{1}, 'overlay', outputpath{2}));
    %%close all
    %%

    %Calculate distance between a pixel and the nearest nonzero pixel;
    %chessboard, cityblock, euclidean, quasi-euclidean
    fprintf("Calculate diameters\n");

    Dist = 2*bwdist(~BW);
    diameters = Dist(SK);

    fprintf("# Morphological Analysis Complete!\n");

    %togglefig('Data')
    if conv > 0
        h = histogram(diameters*conv);
    else
        h = histogram(diameters);
    end
    %hold on
    %% findpeaks(h.Values, h.BinEdges(1:end-1), 'Threshold', 0.01*max(h.Values))
    %% [pks, loc] = findpeaks(h.Values, h.BinEdges(1:end-1), 'Threshold', 0.01*max(h.Values),'Annotate', 'peaks');
    %% [~,i] = max(pks);




    y = [0 0 h.Values];
    x = [h.BinEdges(1)-2 h.BinEdges(1)-1 h.BinEdges(1:end-1)];
    f = fit(x',y','gauss1');

    %hold on
    %plot(f,x,y)
    %ylim([0 inf]);
    %ylabel('Frequency');
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

    %%set(gca,'LooseInset',get(gca,'TightInset'));
    %saveas(gcf, fullfile(outputpath{1}, 'histogram', outputpath{2}));
    %%close all

    dia_img(dia_img == 0) = NaN;
    %%

    %% End of SIMPoly Matlab Method Code
                    
    function saveimg(I, name)
        name = sprintf('%s-matlab.png', name);
        outputpath = fullfile(pwd, 'conversion-out', name);

        imwrite(I, outputpath);
        fprintf('Saved image %s\n', name);
    end

end