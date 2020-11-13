# RDSDS-Server

This is the server for RDSDS, a [GA4GH DRS 1.1](https://ga4gh.github.io/data-repository-service-schemas/preview/release/drs-1.1.0/docs/) implementation. It provides a webservice serving DRS object IDs for data indexed by [RDSDS-indexer](https://github.com/EMBL-EBI-TSI/RDSDS-Indexer). This can be used on its own or as part of the wider GA4GH system for running federated workflows.

An RDSDS server at https://drs-rdsds.tsi.ebi.ac.uk/docs serves DRS object IDs for [EMBL-EBI](http://ebi.ac.uk) datasets. One example is https://drs-rdsds.tsi.ebi.ac.uk/ga4gh/drs/v1/objects/c9290ef86606af6092e3ef837caa5f8885017927f674121809cffef9633d199190a5ef19ab45f42ad620f0e7490c1b3725a7225a254717fa6709a1d72e88bdb4 which serves a whole genome sequence dataset for Sorghum from the [European Variation Archive](https://www.ebi.ac.uk/eva/) with accession number [PRJEB9507](https://www.omicsdi.org/dataset/eva/PRJEB9507).

This is a work in progress. Bug reports and pull requests are welcome!

This work is co-funded by the EOSC-hub project (Horizon 2020) under  Grant number 777536.

## Features

1.  Integrated with ELIXIR AAI for AuthN-Z ([more](https://elixir-europe.org/services/compute/aai))
    
2.  Supports Globus Connect transfer services ([more](https://www.globus.org/))
    
3.  Implements GA4GH Data Repository Standard (DRS) v1.1 ([more](https://github.com/ga4gh/data-repository-service-schemas))
    
4.  Deployable on Kubernetes, tested in Google Cloud

## Roadmap

* API for finding DRS dataset IDs by repository name and accession.
* Integrate RDSDS DRS object IDs with Omics DI.
* Implementation of GA4GH Passports for AuthN-Z.
