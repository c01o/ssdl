{
  description = "Shared Slide Downloader";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }: let
    ssdl = with nixpkgs.legacyPackages.x86_64-linux;
     stdenv.mkDerivation {
      pname = "ssdl";
      version = "0.1.1";

      src = self; 
      buildInputs = with python3Packages; [
        python3
        beautifulsoup4
        img2pdf
        fire
        makeWrapper
      ];

      installPhase = ''
        mkdir -p $out/bin
        cp $src/main.py $out/bin/ssdl
        cp -r $src/lib $out/bin/
        chmod +x $out/bin/ssdl
      '';

      postFixup = ''
        wrapProgram $out/bin/ssdl \
          --prefix PYTHONPATH : "$PYTHONPATH"
      '';

      meta = with nixpkgs.lib; {
        description = "Shared Slide Downloader";
        homepage = "https://github.com/c01o/ssdl";
      };
    };

  in {

    packages.x86_64-linux.ssdl = ssdl;

    defaultPackage.x86_64-linux = ssdl;

    homeManagerModules.ssdl = { pkgs, ... }: {
      home.packages = [ pkgs.ssdl ];
    };
  };
}