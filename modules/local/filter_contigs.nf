process FILTER_CONTIGS {
    tag "$meta.id"
    label 'process_low'

    conda "conda-forge::python=3.9.5"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/pandas:1.5.1_cv1' :
        'biocontainers/pandas:1.5.1_cv1' }"

    input:
    tuple val(meta), path(contigs) 

    output:
    path '*_filtered.tsv'           , emit: filtered_contigs
    path '*_highest_coverage.tsv'   , emit: high_cov_contigs
    path '*_raw.tsv'                , emit: contigs
    

    when:
    task.ext.when == null || task.ext.when
    
    script: // This script is bundled with the pipeline, in nf-core/viralrecon/bin/
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    filter_contigs.py \\
        -i ${contigs} \\
        -l 100 \\
        -c 100

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
