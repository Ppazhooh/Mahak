# Mahak

This release presents the source code and materials used for the experiments in our HotNets'23 paper: "Harnessing ML For Network Protocol Assessment: A Congestion Control Use Case"


## Preparation
To clone this repository, run:

```
git clone https://github.com/Ppazhooh/mahak
```

Many of the tools and programs run by Mahak, inclduing our patched version of Mahimahi, Anaconda , Server anc Client for the experiments, can be installed using `setup.sh` file in `setup` folder.
To run `setup.sh`, in mahak parent folder, use:
```
setup/setup.sh
```



## Running Mahak

To run Mahak, make sure that py3 environment is activated by using `conda activate py3`. Then in the main folder, run 'run_mahak.sh', which runs `mahak_online.py`.
`mahak_online.py` gest the target CC, computation budget, desired metric and the specification of the search space by its input arguments. 
You can use `python mahak_online.py -h` to learn more about input arguments of Mahak.



## What CC schemes Can I Test?
Mahak treats the target CC scheme as blackbox, so there is no limitation to what schemes Mahak can test. You only need to change the `oracle_query` function in  `helper.py`.
This version of code supports kernel based CC schemes such as BBR, Cubic, Vegas and etc.
