SSDL: Shared Slide DownLoader

# What's this
Command to download slides from slideshare / speakerdeck.

# Installation
## Python
- `pip install -r requirements.txt`
- `./main.py`

## Nix
- `nix build -L ".#"`
- `./result/bin/ssdl`

# TIPS
- CLI implemented with [google/python-fire](https://github.com/google/python-fire).
- Download slides into `./slides` by default. Pass `to` args to modify.

# Thanks
-  Referenced [Neelfrost/slideshare-dl](https://github.com/Neelfrost/slideshare-dl) to implement slideshare downloader.
