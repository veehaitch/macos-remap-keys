{
  description = "Remap keys with pure macOS functionality";

  inputs.flake-utils.url = "github:numtide/flake-utils";

  # Also add flake-compat to input and outputs to easily allow updating
  inputs.flake-compat = {
    url = "github:edolstra/flake-compat";
    flake = false;
  };

  outputs = { self, nixpkgs, flake-utils, flake-compat }:
    flake-utils.lib.eachSystem [ "x86_64-darwin" ] (system:
      let
        name = "macos-remap-keys";
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python3;
        dependencies = pypkgs: with pypkgs; [
          pyyaml
        ];
      in
      rec {
        packages."${name}" = python.pkgs.buildPythonPackage {
          name = name;
          version = "0.1";
          src = ./.;
          propagatedBuildInputs = dependencies python.pkgs;
          meta = {
            homepage = "https://github.com/veehaitch/${name}";
            description = self.description;
            maintainers = pkgs.lib.maintainers.veehaitch;
          };
        };

        defaultPackage = self.packages.${system}.macos-remap-keys;

        apps.launchd = {
          type = "app";
          program =
            let drv = pkgs.writeShellScript "remap-launchd" ''
              ${defaultPackage}/bin/remap.py \
                --config ${./config.yaml} \
                --keytables ${./keytables.yaml} \
                --launchd-plist \
                ~/Library/LaunchAgents/ch.veehait.macos-remap-keys.plist
            '';
            in drv.outPath;
        };

        apps.hidutil = {
          type = "app";
          program =
            let drv = pkgs.writeShellScript "remap-launchd" ''
              hidutil property --set \
                `${defaultPackage}/bin/remap.py \
                --config ${./config.yaml} \
                --keytables ${./keytables.yaml} \
                --hidutil-property`
            '';
            in drv.outPath;
        };

        devShell = import ./shell.nix { inherit pkgs; };
      }
    );
}
