# TinyTwin Flags

- `-TP`: Number of taps of UL and DL convolution

## Logging MAC and PHY level metrics

To log any of the below quantities, follow any of the flags below by any non-zero number.

TTI level logging:
- `-SNR`: Log SNR and RSRP
- `-CQI`: Log CQIs
- `-TT`: Log cumulative gNB throughput in  UL and DL both. ALso logs whether MAC ReTxs occur in a given TTI.
- `-MCS`: Logs the MCS of the transmission across a given TTI.
- `-TTI`: Log time between consequent TTIs. 

Will move to the config file soon.

## Files Modified

### UL SNR
**File:** `gnb_scheduler_dlsch.c:672`
```c
if (snrlog) {
    if (sched_ctrl != NULL) {
        fprintf(fpsnr, "TTI Index: %d\n", tti_counter);
        fprintf(fpsnr, "UL SNR: %f\n", (float)(sched_ctrl->pusch_snrx10 / 10.0)); 
        fprintf(fpsnr, "UL ReTx: %d\n", sched_pdsch->dl_harq_pid);
    }
}
```

### UL CQI
**File:** `gnb_scheduler_ulsch.c:753`
```c
if (cqilog) {
    fprintf(fpsnr, "TTI Index: %d\n", tti_counter);
    fprintf(fpsnr, "UL CQI: %d\n", ul_cqi);  
}
```

### UL Throughput
**File:** `gnb_scheduler_ulsch.c:1839`
```c
if (tptlog) {
    fprintf(fpsnr, "TTI Index: %d\n", tti_counter);
    fprintf(fpsnr, "UL TPT: %f\n", UE->ul_thr_ue);  
    // fprintf(fpultpt, "UL ReTx: %d\n", sched_ctrl->retrans_ul_harq.head);
}
```

### UL MCS
**File:** `gnb_scheduler_ulsch.c:1901`
```c
if (mcslog) {
    fprintf(fpsnr, "TTI Index: %d\n", tti_counter);
    fprintf(fpsnr, "UL MCS: %d\n", sched_pusch->mcs);  
}
```

### DL RSRP
**File:** `csi_rx.c:258`
```c
if (snrlog) {
    fprintf(fprsrp, "TTI Count: %d\n", tti_counter);
    fprintf(fprsrp, "RSRP: %i\n", *rsrp_dBm);  
}
```

### DL MCS
**File:** `gnb_scheduler_dlsch.c:737`
```c
if (mcslog) {
    fprintf(fprsrp, "TTI Count: %d\n", tti_counter);
    fprintf(fprsrp, "DL MCS: %d\n", sched_ctrl->dl_bler_stats.mcs);  
    fprintf(fprsrp, "DL BLER_LB : %f\n", sched_ctrl->dl_bler_stats.bler);  
}
```

### DL Throughput
**File:** `gnb_scheduler_dlsch.c:672`
```c
if (snrlog) {
    if (sched_ctrl != NULL) {
        fprintf(fpsnr, "TTI Index: %d\n", tti_counter);
        fprintf(fpsnr, "UL SNR: %f\n", (float)(sched_ctrl->pusch_snrx10 / 10.0)); 
        fprintf(fpsnr, "UL ReTx: %d\n", sched_pdsch->dl_harq_pid);
    }
}
```
