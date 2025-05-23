## EdgeRIC class and wrapper
Folder location: ``executables/edgeric/``  
important files: ``edgeric.cpp, wrapper.cpp``  

## Metrics Logging
Location: ``openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c``  - TTI, dl_buffer, tx_bytes, UL snr, cqi, dl_tbs  
### Todo: Packet drops - add to edgeric
Update logging (printmyvariable) and edgeric protobufs  
File Location: ````openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c`` 
```bash
## For reference - look at branch parallel_fast_conv
  // ///////////////////////////////////////////////////////////////
      NR_bler_stats_t *bler_stats = &sched_ctrl->dl_bler_stats;
      int num_dl_retx = (int)(stats->rounds[1] - bler_stats->rounds[1]);
      fprintf(fpretx, "%d %d\n", num_dl_retx, UE->rnti);
      // /////////////////////////////////////////////////////////////////
```



## MCS control
File Location: ``openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c``    
```bash
static void pf_dl(module_id_t module_id,
                  frame_t frame,
                  sub_frame_t slot,
                  NR_UE_info_t **UE_list,
                  int max_num_ue,
                  int n_rb_sched,
                  uint16_t *rballoc_mask)


sched_pdsch->mcs = get_mcs_from_bler_new(UE->rnti,bo, stats, &sched_ctrl->dl_bler_stats, max_mcs, frame);
```
File location: openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c  
```bash
int get_mcs_from_bler_new(int rnti,         /////////////////////// add
                      const NR_bler_options_t *bler_options,
                      const NR_mac_dir_stats_t *stats,
                      NR_bler_stats_t *bler_stats,
                      int max_mcs,
                      frame_t frame)
```

## Scheduling Control
Location: ``openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_dlsch.c``    
```bash
## File location: openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c
nr_find_nb_rb_new(rnti,  /////////////// add
                  sched_pdsch->Qm,
                  sched_pdsch->R,
                  1, // no transform precoding for DL
                  sched_pdsch->nrOfLayers,
                  tda_info->nrOfSymbols,
                  sched_pdsch->dmrs_parms.N_PRB_DMRS * sched_pdsch->dmrs_parms.N_DMRS_SLOT,
                  sched_ctrl->num_total_bytes + oh,
                  min_rbSize,
                  max_rbSize,
                  rb_total_num, /////////////////add
                  &TBS,
                  &rbSize);
```
