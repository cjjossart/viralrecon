process PITYPE_WEB {
    tag "$meta.id"
    label 'process_low'

    conda "conda-forge::python=3.9.5"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/pandas:1.5.1_cv1' :
        'cjjossart/pitype-web:latest' }"

    input:
    tuple val(meta), val(contig), val(length), val(coverage), val(sequence)

    output:
    // Tuple with id, csv files,
    // Tuple with id, reference value
    path '*_pass_nt_pitype.csv'           , emit: pass_nt_pitype
    path '*_filtered_pitype.csv'          , emit: filtered_pitype
    path '*_raw_pitype.csv'               , emit: raw_pitype
    path '*_ref_pitype.csv'               , emit: ref_pitype

    when:
    task.ext.when == null || task.ext.when

    script: // This script is bundled with the pipeline, in nf-core/viralrecon/bin/
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    pitype_web.py \\
        -q ${sequence} \\
        -s ${prefix} \\
        -c ${contig}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
