process TRIQLER {
    label 'process_medium'

    container "${ workflow.containerEngine == 'singularity' ?
        'docker://cauldron/triqler:1.0.3' :
        'cauldron/triqler:1.0.3' }"

    input:
    val input_format
    path input_file
    path file_list_file
    val fold_change_eval
    val decoy_pattern
    val min_samples
    val missing_value_prior
    val num_threads
    val use_ttest
    val write_spectrum_quants
    val write_protein_posteriors
    val write_group_posteriors
    val write_fold_change_posteriors

    output:
    
    path "proteins.tsv", emit: protein_results, optional: true
    path "condition_mapping.tsv", emit: condition_mapping, optional: true
    path "triqler_input.tsv", emit: triqler_input, optional: true
    path "spectrum_quants.tsv", emit: spectrum_quants, optional: true
    path "protein_posteriors.tsv", emit: protein_posteriors, optional: true
    path "group_posteriors.tsv", emit: group_posteriors, optional: true
    path "fold_change_posteriors.tsv", emit: fold_change_posteriors, optional: true
    path "versions.yml", emit: versions

    script:
    def args = task.ext.args ?: ''
    """
    # Build arguments dynamically to match CauldronGO PluginExecutor logic
    ARG_LIST=()

    
    # Mapping for num_threads
    VAL="$num_threads"
    if [ -n "\$VAL" ] && [ "\$VAL" != "null" ] && [ "\$VAL" != "[]" ]; then
        ARG_LIST+=("--num_threads" "\$VAL")
    fi
    
    # Mapping for write_spectrum_quants
    VAL="$write_spectrum_quants"
    if [ -n "\$VAL" ] && [ "\$VAL" != "null" ] && [ "\$VAL" != "[]" ]; then
        if [ "\$VAL" = "true" ]; then
            ARG_LIST+=("--write_spectrum_quants")
        fi
    fi
    
    # Mapping for write_group_posteriors
    VAL="$write_group_posteriors"
    if [ -n "\$VAL" ] && [ "\$VAL" != "null" ] && [ "\$VAL" != "[]" ]; then
        if [ "\$VAL" = "true" ]; then
            ARG_LIST+=("--write_group_posteriors")
        fi
    fi
    
    # Mapping for input_format
    VAL="$input_format"
    if [ -n "\$VAL" ] && [ "\$VAL" != "null" ] && [ "\$VAL" != "[]" ]; then
        ARG_LIST+=("--input_format" "\$VAL")
    fi
    
    # Mapping for min_samples
    VAL="$min_samples"
    if [ -n "\$VAL" ] && [ "\$VAL" != "null" ] && [ "\$VAL" != "[]" ]; then
        ARG_LIST+=("--min_samples" "\$VAL")
    fi
    
    # Mapping for use_ttest
    VAL="$use_ttest"
    if [ -n "\$VAL" ] && [ "\$VAL" != "null" ] && [ "\$VAL" != "[]" ]; then
        if [ "\$VAL" = "true" ]; then
            ARG_LIST+=("--use_ttest")
        fi
    fi
    
    # Mapping for write_protein_posteriors
    VAL="$write_protein_posteriors"
    if [ -n "\$VAL" ] && [ "\$VAL" != "null" ] && [ "\$VAL" != "[]" ]; then
        if [ "\$VAL" = "true" ]; then
            ARG_LIST+=("--write_protein_posteriors")
        fi
    fi
    
    # Mapping for write_fold_change_posteriors
    VAL="$write_fold_change_posteriors"
    if [ -n "\$VAL" ] && [ "\$VAL" != "null" ] && [ "\$VAL" != "[]" ]; then
        if [ "\$VAL" = "true" ]; then
            ARG_LIST+=("--write_fold_change_posteriors")
        fi
    fi
    
    # Mapping for input_file
    VAL="$input_file"
    if [ -n "\$VAL" ] && [ "\$VAL" != "null" ] && [ "\$VAL" != "[]" ]; then
        ARG_LIST+=("--input_file" "\$VAL")
    fi
    
    # Mapping for file_list_file
    VAL="$file_list_file"
    if [ -n "\$VAL" ] && [ "\$VAL" != "null" ] && [ "\$VAL" != "[]" ]; then
        ARG_LIST+=("--file_list_file" "\$VAL")
    fi
    
    # Mapping for fold_change_eval
    VAL="$fold_change_eval"
    if [ -n "\$VAL" ] && [ "\$VAL" != "null" ] && [ "\$VAL" != "[]" ]; then
        ARG_LIST+=("--fold_change_eval" "\$VAL")
    fi
    
    # Mapping for decoy_pattern
    VAL="$decoy_pattern"
    if [ -n "\$VAL" ] && [ "\$VAL" != "null" ] && [ "\$VAL" != "[]" ]; then
        ARG_LIST+=("--decoy_pattern" "\$VAL")
    fi
    
    # Mapping for missing_value_prior
    VAL="$missing_value_prior"
    if [ -n "\$VAL" ] && [ "\$VAL" != "null" ] && [ "\$VAL" != "[]" ]; then
        ARG_LIST+=("--missing_value_prior" "\$VAL")
    fi
    
    python /app/triqler_runner.py \
        "\${ARG_LIST[@]}" \
        --output_dir . \
        \${args:-}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        Triqler Protein Quantification: 1.0.3
    END_VERSIONS
    """
}
