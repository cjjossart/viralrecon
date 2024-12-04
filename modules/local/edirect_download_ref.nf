process EDIRECT_DOWNLOAD_REF {
    //tag "$meta.id"
    label 'process_low'

    conda "conda-forge::python=3.9.5"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/pandas:1.5.1_cv1' :
        'cjjossart/edirect:latest' }"

    input:
    tuple val(meta), val(reference)

    output:
    tuple val(meta), path('*.fasta')          , emit: pitype_reference
    
    when:
    task.ext.when == null || task.ext.when

    script: // This script is bundled with the pipeline, in nf-core/viralrecon/bin/
    """
    esearch -db nucleotide -query ${reference} | efetch -format fasta > ${reference}.fasta

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
