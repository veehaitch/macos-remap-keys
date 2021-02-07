{ pkgs ? import <nixpkgs> { } }:
with pkgs;
let
  pythonEnv = python3.withPackages (ps: with ps; [
    ipython
    pyyaml
  ]);
in
mkShell {
  name = "macos-remap-keys-shell";
  buildInputs = [
    pythonEnv
    black
  ];
}
