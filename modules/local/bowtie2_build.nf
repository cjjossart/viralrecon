process BOWTIE2_BUILD {
    tag "$meta.id"
    label 'process_high'

    conda "bioconda::bowtie2=2.4.4"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/bowtie2:2.4.4--py39hbb4e92a_0' :
        'quay.io/biocontainers/bowtie2:2.4.4--py39hbb4e92a_0' }"

    input:
    tuple val(meta), path(fasta)

    output:
    tuple val(meta), path('bowtie2_*_index')    , emit: index
    path "versions.yml"                 , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    //def index_dir = task.ext.index_dir ?: "bowtie2/${meta}"
    //def prefix = task.ext.prefix ?: "${meta.id}"
    """
    mkdir bowtie2_${meta}_index
    bowtie2-build $args --threads $task.cpus -f ${fasta} bowtie2_${meta}_index/${fasta.baseName}
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        bowtie2: \$(echo \$(bowtie2 --version 2>&1) | sed 's/^.*bowtie2-align-s version //; s/ .*\$//')
    END_VERSIONS
    """
}