{
  description = "Async API connector for PT Sandbox instances";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:nix-community/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    pyproject-nix,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};

        # python setup
        python =
          pkgs.python3.override {
          };

        pypkgs = python.pkgs;
        project = pyproject-nix.lib.project.loadUVPyproject {
          projectRoot = ./.;
        };
        projectAttrs = project.renderers.buildPythonPackage {inherit python;};
      in {
        packages = {
          py-ptsandbox = python.pkgs.buildPythonPackage projectAttrs;
          default = self.packages.${system}.py-ptsandbox;
        };
      }
    );
}
