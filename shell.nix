{ pkgs ? import <nixpkgs> {} }:
with pkgs; pkgs.mkShell {
  buildInputs =[
    python3 
    python3.pkgs.pip
    python3.pkgs.setuptools
    python3.pkgs.psycopg2
  ];
  shellHook = ''
    export LD_LIBRARY_PATH=${stdenv.cc.cc.lib}/lib/
    export PIP_PREFIX=$(pwd)/_build/pip_packages
    export PYTHONPATH="$PIP_PREFIX/${pkgs.python3.sitePackages}:$PYTHONPATH"
    export PATH="$PIP_PREFIX/bin:$PATH"
    unset SOURCE_DATE_EPOCH
    source .venv/bin/activate
    pip install -r requirement.txt
  '';
}
