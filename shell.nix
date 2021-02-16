let
  flakeLock = builtins.fromJSON (builtins.readFile ./flake.lock);
  flake-compat-rev = fetchTarball {
    url = "https://github.com/edolstra/flake-compat/archive/${flakeLock.nodes.flake-compat.locked.rev}.tar.gz";
    sha256 = flakeLock.nodes.flake-compat.locked.narHash;
  };
  flake-compat = import flake-compat-rev { src = ./.; };
in
flake-compat.shellNix
