process SEQKIT_TAB {
    tag "$meta.id"
    label 'process_low'


    conda "bioconda::seqkit=2.4.0"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/seqkit:2.4.0--h9ee0642_0':
        'staphb/seqkit:latest' }"

    input:
    tuple val(meta), path(contigs)

    output:
    tuple val(meta), path('*.contigs.tsv')         , emit: contigs_tsv
    path "versions.yml"                            , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    
    """
    seqkit \\
        fx2tab \\
        $args \\
        --threads $task.cpus \\
        ${contigs} \\
        -o ${prefix}.contigs.tsv \\

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        seqkit: \$( seqkit version | sed 's/seqkit v//' )
    END_VERSIONS
    """
}