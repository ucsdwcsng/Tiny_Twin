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

## Files Modified

### UL SNR: `gnb_scheduler_dlsch.c:672`
    ```
    if (snrlog){
        if (sched_ctrl != NULL) {
            fprintf(fpsnr, "TTI Index: %d\n", tti_counter);
            fprintf(fpsnr, "UL SNR: %f\n", (float)(sched_ctrl->pusch_snrx10 / 10.0)); 
            fprintf(fpsnr, "UL ReTx: %d\n", sched_pdsch->dl_harq_pid);
        }
    }
    ```

### UL CQI: `gnb_scheduler_ulsch.c:753`
    ```
    if (cqilog){
        fprintf(fpsnr, "TTI Index: %d\n", tti_counter);
        fprintf(fpsnr, "UL CQI: %d\n", ul_cqi);  
    }
    ```    

### UL TPT: `gnb_scheduler_ulsch.c:1839`
    ```
    if (tptlog){
        fprintf(fpsnr, "TTI Index: %d\n", tti_counter);
        fprintf(fpsnr, "UL TPT: %f\n", UE->ul_thr_ue);  
        // fprintf(fpultpt, "UL ReTx: %d\n", sched_ctrl->retrans_ul_harq.head);
    }
    ```

### UL MCS: `gnb_scheduler_ulsch.c:1901`
    ```
    if (mcslog){
        fprintf(fpsnr, "TTI Index: %d\n", tti_counter);
        fprintf(fpsnr, "UL MCS: %d\n", sched_pusch->mcs);  
    }
    ```

### DL RSRP: `csi_rx.c:258`
    ```
    if (snrlog){
        fprintf(fprsrp, "TTI Count: %d\n", tti_counter);
        fprintf(fprsrp, "RSRP: %i\n", *rsrp_dBm);  
    }
    ``` 

### DL MCS: `gnb_scheduler_dlsch.c:737`
    ```
    if (mcslog){
    fprintf(fprsrp, "TTI Count: %d\n", tti_counter);
    fprintf(fprsrp, "DL MCS: %d\n", sched_ctrl->dl_bler_stats.mcs);  
    fprintf(fprsrp, "DL BLER_LB : %f\n", sched_ctrl->dl_bler_stats.bler);  
    }
    ```  

### DL TPT: `gnb_scheduler_dlsch.c:672`
    ```
    if (snrlog){
        if (sched_ctrl != NULL) {
            fprintf(fpsnr, "TTI Index: %d\n", tti_counter);
            fprintf(fpsnr, "UL SNR: %f\n", (float)(sched_ctrl->pusch_snrx10 / 10.0)); 
            fprintf(fpsnr, "UL ReTx: %d\n", sched_pdsch->dl_harq_pid);
        }
        }
    ```           