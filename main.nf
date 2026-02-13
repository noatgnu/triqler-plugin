#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

include { TRIQLER } from './modules/local/triqler/main'

workflow PIPELINE {
    main:
    TRIQLER (
        params.input_file ? Channel.fromPath(params.input_file).collect() : Channel.of([]),
        Channel.value(params.input_format ?: ''),
        params.file_list_file ? Channel.fromPath(params.file_list_file).collect() : Channel.of([]),
        Channel.value(params.fold_change_eval ?: ''),
        Channel.value(params.decoy_pattern ?: ''),
        Channel.value(params.min_samples ?: ''),
        Channel.value(params.missing_value_prior ?: ''),
        Channel.value(params.num_threads ?: ''),
        Channel.value(params.use_ttest ?: ''),
        Channel.value(params.write_spectrum_quants ?: ''),
        Channel.value(params.write_protein_posteriors ?: ''),
        Channel.value(params.write_group_posteriors ?: ''),
        Channel.value(params.write_fold_change_posteriors ?: ''),
    )
}

workflow {
    PIPELINE ()
}
