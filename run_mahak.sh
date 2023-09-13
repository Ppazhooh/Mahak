rm traces/*
python mahak_online.py -cc cubic -budget 20 -metric first_power -buffer 2,200,4 -mRTT 5,50,5 -bw 2,20,5 -change 0.1,2,0.1
