{
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forAllSystems =
        function:
        nixpkgs.lib.genAttrs systems (
          system:
          function (
            import nixpkgs {
              inherit system;
              config.allowUnfree = true;
            }
          )
        );
    in
    {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            vagrant
            python39
          ];

          env = { };

          shellHook = ''
            if [ ! -d ./.venv ]; then
              python3 -m venv .venv
              source ./.venv/bin/activate
              pip install "jinja2<3.1"
              pip install "ansible==2.9.0"
            else
              source ./.venv/bin/activate
            fi
          '';
        };
      });
    };
}
