# Acupuncture Webapp v0.1
By [William Gardner](https://github.com/wg4568/), written for _@yongsubchung_ on Fiverr

## Installation

To set up your system, you will need to do the following

- Install Python3.7 from their [website](https://www.python.org/)
- Install requirements by running `python -m pip install -r requirements.txt`

## Files

### Most important

You will need to use these files!

- `README.md` this file, for help and info
- `config.json` options and configuration
- `requirements.txt` required packages
- `main.py` run this to start the application

## Configuration

See `config.json` to configure the bot.

The config file is formatted with the parameter name on the left, and it's value on the right. Do NOT touch the name on the left! This will break the bot. Instead change the value on the right to tweak your bot.

    "name": "value (change this!)"

Values that are text (as opposed to a number) should be surrounded by double quotes, as shown above.

 Configuration parameters are described below.

- `ip` where webapp will bind itself
- `port` webapp port, note port 80 requires elevation
- `debug` run in debug mode (insecure!)