#!/bin/sh

set -ex

cd "$(dirname "$0")"

# Attention à bien charger les submodules avant de build
cd lib/hash-sigs
make -j4
cd ../../

# build chal
mkdir -p bin
gcc src-chal/*.c ./lib/hash-sigs/hss_lib_thread.a -I ./lib/hash-sigs -lcrypto -lpthread -o bin/chal

exit 0
