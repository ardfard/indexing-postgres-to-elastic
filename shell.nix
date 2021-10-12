{ pkgs ? import <nixpkgs> {} }:
with pkgs; 
pkgs.mkShell {
  buildInputs =[
    python38 
    python38.pkgs.pip
    python38.pkgs.setuptools
    python38.pkgs.psycopg2
    python38.pkgs.elasticsearch
  ];
  shellHook = ''
    export LD_LIBRARY_PATH=${stdenv.cc.cc.lib}/lib/
    export PIP_PREFIX=$(pwd)/_build/pip_packages
    export PYTHONPATH="$PIP_PREFIX/${pkgs.python38.sitePackages}:$PYTHONPATH"
    export PATH="$PIP_PREFIX/bin:$PATH"
    unset SOURCE_DATE_EPOCH
    source .venv/bin/activate
    pip install -r requirements.txt
  '';
}
