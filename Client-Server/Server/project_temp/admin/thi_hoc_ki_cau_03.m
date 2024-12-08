clc
clear all
x=-2*pi:0.01:2*pi;
f=cos(x.^2);
g=sin(x.^2);
hold on
plot(x,f,'r')
plot(x,g,'b')