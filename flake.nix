{
  description = "Async API connector for PT Sandbox instances";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    pyproject-nix.url = "github:nix-community/pyproject.nix";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    nixpkgs,
    pyproject-nix,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};

        # python setup
        python = pkgs.python3.override {
        };

        pypkgs = python.pkgs;
        project = pyproject-nix.lib.project.loadPDMPyproject {
          projectRoot = ./.;
        };
      in rec {
        packages = {
          py-ptsandbox = let
            attrs = project.renderers.buildPythonPackage {inherit python;};
          in
            python.pkgs.buildPythonPackage attrs;
        };

        defaultPackage = packages.py-ptsandbox;
      }
    );
}
