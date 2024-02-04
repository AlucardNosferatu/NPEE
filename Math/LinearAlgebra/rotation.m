clc;
clear;

a = [1, 1, 10]';
tx = 1 * (pi / 2);
ty = 1 * (pi / 2);
tz = 1 * (pi / 2);

rx = [1, 0, 0; 0, cos(tx), -sin(tx); 0, sin(tx), cos(tx)];
disp(rx);
ry = [cos(ty), 0, sin(ty); 0, 1, 0; -sin(ty), 0, cos(ty)];
disp(ry);
rz = [cos(tz), -sin(tz), 0; sin(tz), cos(tz), 0; 0, 0, 1];
disp(rz);

ro = rz * ry * rx;
ri = rx * ry * rz;

ato = ro * a;
disp(ato);
ati = ri * a;
disp(ati);
