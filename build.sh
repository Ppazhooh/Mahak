g++ src/client.c -o client
g++ -pthread src/server-mahimahi.cc src/flow.cc -o server-mahimahi -std=c++11 -Wno-return-type