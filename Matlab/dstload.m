% File: dstload.m
% Purpose: Load data from .dst distribution files
% Created: 2018-04-19 Matt Easton, Peking University

function outputdata = dstload (dstfilename)
% Load a .dst file into memory
%
% Output data is:
%   x   (mm)
%   x'  (mrad)
%   y   (mm)
%   y'  (mrad)
%   phi (rad)
%   W   (MeV)

% Open the file
dstfile = fopen(dstfilename);

% Read the headers
dst_header = fread(dstfile, 2, 'char'); %#ok<NASGU>
dst_Npt    = fread(dstfile, 1, 'int');
dst_Ibeam  = fread(dstfile, 1, 'double');
dst_Freq   = fread(dstfile, 1, 'double');
dst_spacer = fread(dstfile, 1, 'char'); %#ok<NASGU>

% Load the particle data
dst_particles = ones(6, dst_Npt);
for i = 1:dst_Npt
    dst_particles(:, i) = fread(dstfile, 6, 'double');
end %if

% Close the file
fclose(dstfile);

% Write general values
fprintf('Number of particles: %6.0f\n', dst_Npt);
fprintf('Beam current:        %9.2f mA\n', dst_Ibeam);
fprintf('Beam frequency:      %9.2f MHz\n', dst_Freq);

% Save particle data
outputdata = dst_particles;

% Convert units
outputdata(1,:) = outputdata(1,:) * 10;   % convert cm to mm
outputdata(2,:) = outputdata(2,:) * 1000; % convert rad to mrad
outputdata(3,:) = outputdata(3,:) * 10;   % convert cm to mm
outputdata(4,:) = outputdata(4,:) * 1000; % convert rad to mrad

end %function dstload