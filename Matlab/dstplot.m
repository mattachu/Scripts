% File: dstplot.m
% Purpose: Plot data from .dst distribution files
% Created: 2018-04-19 Matt Easton, Peking University

function h = dstplot (plottype, particledata)
% Plot data loaded from a .dst file
%
% Plot types:
%   'x'       x - x'
%   'y'       y - y'
%   'xy'      x - y
%   'phase'   phi - W
%   'energy'  Energy histogram
%
% Input data is:
%   x   (mm)
%   x'  (mrad)
%   y   (mm)
%   y'  (mrad)
%   phi (rad)
%   W   (MeV)

switch plottype
    case 'x'
        h = dstplot_x(particledata);
    case 'y'
        h = dstplot_y(particledata);
    case 'xy'
        h = dstplot_xy(particledata);
    case 'phase'
        h = dstplot_phase(particledata);
    case 'energy'
        h = dstplot_energy(particledata);
    otherwise
        disp('Invalid plot type')
end %switch

end %function dstplot

function h = dstplot_points(xdata, ydata)

h = plot(xdata, ydata);
h.LineStyle = 'none';
h.Marker = '.';
h.MarkerSize = 1;

end %function dstplot_points

function h = dstplot_hist(plotdata)

h = histogram(plotdata);

end %function dstplot_hist

function h = dstplot_x(particledata)

h = dstplot_points(particledata(1,:), particledata(2,:));
xlabel('x (mm)');
ylabel('x'' (mrad)');

end %function dstplot_x

function h = dstplot_y(particledata)

h = dstplot_points(particledata(3,:), particledata(4,:));
xlabel('y (mm)');
ylabel('y'' (mrad)');

end %function dstplot_y

function h = dstplot_xy(particledata)

h = dstplot_points(particledata(1,:), particledata(3,:));
xlabel('x (mm)');
ylabel('y (mm)');

end %function dstplot_xy

function h = dstplot_phase(particledata)

h = dstplot_points(particledata(5,:), particledata(6,:));
xlabel('phi (rad)');
ylabel('W (MeV)');

end %function dstplot_phase

function h = dstplot_energy(particledata)

h = dstplot_hist(particledata(6,:));
xlabel('W (MeV)');

end %function dstplot_energy
