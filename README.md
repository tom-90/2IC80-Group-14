This tool has been developed for the 2IC80 Lab on offensive computer security course of the TU/e.
It contains an arp-poisoning attack, combined with dns-spoofing and SSL-stripping.

# How to use

The easiest way to use the tool is by executing the binary located  at `dist/linux/main`. This is a single executable, containg all project code, dependencies and the Python 3 runtime environment. By using this executable, you do not have to install any other dependencies on your system.

It is also possible to run from the Python source code. For this, you will need to install all dependencies in the `requirements.txt` file, by running `pip3 install -r requirements.txt`. After installing the depenencies, the `src/main.py` file can be executed.

There are a few command line arguments available when running the program:
```
usage: [-h] [-c CONFIG] [-l LOG_FILE] [-d] [-v]

Perform ARP spoof, DNS spoof and log HTTP requests

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        yaml config file (default: prompt for options)
  -l LOG_FILE, --log-file LOG_FILE
                        file where logs should be saved
  -d, --disable-http-forward
                        disable the forwarding of HTTP traffic to HTTPS (this allows you to run your own webserver to serve the user
                        a different spoofed website)
  -v, --verbose         Enable verbose logging
```

The most important of these options is the `-c` option for providing a configuration file. When this option is provided, all settings will be read from the file. If not provided, you will be prompted to choose options for the attack. An example configuration file can be found in `example_config.yml`.