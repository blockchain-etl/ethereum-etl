# Ethereum Classic

For getting ETC csv files, make sure you pass in the `--chain classic` param where it's required for the scripts you want to export. 
ETC won't run if your `--provider-uri` is Infura. It will provide a warning and change the provider-uri to `https://ethereumclassic.network` instead. For faster performance, run a client instead locally for classic such as `parity chain=classic` and Geth-classic.