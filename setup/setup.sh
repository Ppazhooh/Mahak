echo "------------------------ Updating this Instance ------------------------"
sudo apt update
sudo apt install -y vim htop
sudo apt install -y openssh-server
sudo apt install -y git
main_directory=$(pwd)

./build.sh

mkdir -p predictions
mkdir -p traces
mkdir -p logs


# Install Mahimahi
cd ~
echo "------------------------ Mahimahi ------------------------"
sudo apt-get install build-essential git debhelper autotools-dev dh-autoreconf iptables protobuf-compiler libprotobuf-dev pkg-config libssl-dev dnsmasq-base ssl-cert libxcb-present-dev libcairo2-dev libpango1.0-dev iproute2 apache2-dev apache2-bin iptables dnsmasq-base gnuplot iproute2 apache2-api-20120211 libwww-perl
git clone https://github.com/ravinet/mahimahi
cd mahimahi

#echo "Patch Mahimahi here!"
cp $main_directory/mahimahi_patches/highbdp.patch ~/mahimahi
patch -p1 < highbdp.patch
./autogen.sh && ./configure && make
sudo make install
sudo sysctl -w net.ipv4.ip_forward=1

# Install Anaconda
echo "----------------------Anaconda-------------------------"
wget -P ~ https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
bash ~/Anaconda3-2021.11-Linux-x86_64.sh
source ~/anaconda3/bin/activate
conda env create -f $main_directory/envs/py2.yml
conda env create -f $main_directory/envs/py3.yml