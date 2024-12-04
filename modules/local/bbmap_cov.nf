process BBMAP_COV {
    tag "$meta.id"
    label 'process_medium'

    conda "bioconda::bbmap=39.01 bioconda::samtools=1.16.1 pigz=2.6"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/mulled-v2-008daec56b7aaf3f162d7866758142b9f889d690:e8a286b2e789c091bac0a57302cdc78aa0112353-0' :
        'staphb/bbtools:latest' }"

    input:
    tuple val(meta), path(fastq)
     tuple val(meta), path(contigs)
    output:
    tuple val(meta), path("*covstats.tsv"), emit: covstats
    tuple val(meta), path("*.log"), emit: covstats_log
    path "versions.yml"           , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"

    input = meta.single_end ? "in=${fastq}" : "in=${fastq[0]} in2=${fastq[1]}"
    """
    reformat.sh \\
        in= ${contigs} \\
        out= filtered_${contigs} \\
        minlegth=100 \\
        
    bbmap.sh \\
        $input \\
        ref=${contigs} \\
        covstats=${prefix}_covstats.tsv \\
        $args \\
        threads=$task.cpus \\
        -Xmx${task.memory.toGiga()}g \\
        &> ${prefix}.bbmap.log

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        bbmap: \$(bbversion.sh | grep -v "Duplicate cpuset")
        samtools: \$(echo \$(samtools --version 2>&1) | sed 's/^.*samtools //; s/Using.*\$//')
        pigz: \$( pigz --version 2>&1 | sed 's/pigz //g' )
    END_VERSIONS
    """
}
