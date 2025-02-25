# TinyTwin Flags

- `-T`: Number of taps of UL and DL convolution

## Logging MAC and PHY level metrics

To log any of the below quantities, follow any of the flags below by any non-zero number.

TTI level logging:
- `-S`: Log SNR and RSRP
- `-Q`: Log CQIs
- `-P`: Log cumulative gNB throughput in  UL and DL both. ALso logs whether MAC ReTxs occur in a given TTI.
- `-X`: Logs the MCS of the transmission across a given TTI.

Will move to the config file soon.