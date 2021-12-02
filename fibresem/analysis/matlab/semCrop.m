function imgout = semCrop(imgin, barHeight, boolSquare)

% barheight = 0.11;

[imgHeight, imgWidth] = size(imgin);

newHeight = round(imgHeight * (1 - barHeight));

if boolSquare
    left = round((imgWidth - newHeight) / 2);
    right = imgWidth - left;

    imgout = imgin(1:newHeight, left:right);
else
    imgout = imgin(1:newHeight, :);
end

end

