#!/bin/bash

WORDS="${@:2}"

if [[ "$1" = "-d" ]]; then
  echo -e "Deleting the following words from wordlist.txt:\n${WORDS}"
  for i in $WORDS; do
    sed -i -r "/^${i}$/d" wordlist.txt
  done
elif [[ "$1" = "-a" ]]; then
  echo -e "Adding the following words to wordlist.txt:\n${WORDS}"
  for i in $WORDS; do
    echo "$i" >> wordlist.txt
  done
fi

echo -e "\nSorting wordlist..."
sort -u wordlist.txt | awk 'NF>0' > tmp && mv tmp wordlist.txt
echo "Done."
