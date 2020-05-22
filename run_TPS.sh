./scripts/run \
   --network data/networks/input-network.tsv \
   --timeseries data/timeseries/median-time-series.tsv \
   --firstscores data/timeseries/p-values-first.tsv \
   --prevscores data/timeseries/p-values-prev.tsv \
   --partialmodel data/resources/kinase-substrate-interactions.sif \
   --peptidemap data/timeseries/peptide-mapping.tsv \
   --source EGF_HUMAN \
   --threshold 0.01