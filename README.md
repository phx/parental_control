![logo](./logo.png?raw=true)

# Parental Control Squid

**Dependencies:**

- any *nix OS
- squid forward proxy (local or remote)
- python3 (all native library)
- bash (not `sh` -- optional for keeping the list sorted via `sortlist.sh`)

This is a python script that I wrote in order to help keep an eye on my kids.  They are young, but they have their own computers, and I'm not very fond of commercial spyware, so I decided to roll my own.

The script is compatible with any local or remote host running Squid forward proxy that you want to monitor for URL content.  Setting up Squid is beyond the scope of this guide, so please feel free to Google
that on your own.

Basically, I have both of my kid's WiFi MAC addresses in a LAN NAT rule that forwards all outgoing HTTP/HTTPS traffic to my squid forward proxy.

I found a list of really bad words (some not necessarily bad, but stuff that my wife and I would want to know about if they were interested in finding out about).

I have the script running on my management server via cronjob every hour, and if it finds any interesting traffic from the kids' laptops, it will send a text to my wife and myself.

The wordlist is not exhaustive, and I have removed numerous terms that caused false positives, but it seems to work very well. 

## sortlist.sh

This is a bash script used for adding and removing terms from `wordlist.txt`, while at the same time, keeping that file deduplicated and organized.

### Examples:

Remove `weed` from `wordlist.txt` because it causes a false positive for `seaweed flavored pringles`:

`./sortlist.sh -d weed`

Remove `puss`, `butt`, and `pee` from `wordlist.txt` because of false positives containing `button`, `shopee`, and a weird Dragonball Z URL -- additionally, we will remove `gspot`, because of false positives from `blogspot.com`:

`./sortlist.sh -d puss butt pee gspot`

Let's not let ourselves get too comfortable, let's go ahead and add a few more specific/explicit entries:

`./sortlist -a pussy pussies butts peeing g-spot`

## Running the main script:

Simply run `./parental_control.py`, and everything will work smoothly, as long as you have the `config.ini` populated correctly.

Alternately, if you are testing some things and don't want email/texts to be sent, you can also run `./parental_control.py -noemail`.

## Details:

This should run on pretty much any OS except for Windows.

If you have any questions, please feel free to submit an issue.

