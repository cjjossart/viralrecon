//
// Process contigs from enterovirus samples, type using pitype, map to pitype reference and build consensus of VP1 region
//

include { BBMAP_COV                             } from '../../modules/local/bbmap_cov'
include { SEQKIT_TAB                            } from '../../modules/local/seqkit_tab'
include { FILTER_CONTIGS                        } from '../../modules/local/filter_contigs'
include { PITYPE_WEB                            } from '../../modules/local/pitype_web'
include { EDIRECT_DOWNLOAD_REF                  } from '../../modules/local/edirect_download_ref'
include { BOWTIE2_BUILD                         } from '../../modules/local/bowtie2_build'
include { BOWTIE2_ALIGN                         } from '../../modules/local/bowtie2_align'
include { SAMTOOLS_SORT                         } from '../../modules/nf-core/samtools/sort/main'
include { SAMTOOLS_INDEX                        } from '../../modules/nf-core/samtools/index/main'
include { SAMTOOLS_STATS                        } from '../../modules/nf-core/samtools/stats/main'
include { SAMTOOLS_FLAGSTAT                     } from '../../modules/nf-core/samtools/flagstat/main'
include { SAMTOOLS_IDXSTATS                     } from '../../modules/nf-core/samtools/idxstats/main'
include { SAMTOOLS_CONSENSUS                    } from '../../modules/local/samtools_consensus'
include { IVAR_CONSENSUS                        } from '../../modules/nf-core/ivar/consensus/main'
include { SEQKIT_TAB as SEQKIT_TAB_2            } from '../../modules/local/seqkit_tab'
include { FILTER_CONTIGS as FILTER_CONTIGS_2    } from '../../modules/local/filter_contigs'
include { PITYPE_WEB as PITYPE_WEB_2            } from '../../modules/local/pitype_web'
include { FASTQ_ALIGN_BOWTIE2                   } from '../../subworkflows/nf-core/fastq_align_bowtie2/main'
include { BAM_STATS_SAMTOOLS                    } from '../../subworkflows/nf-core/bam_stats_samtools/main'


workflow ENTERO_PITYPE {

    take:
    fastp_reads     // channel: [ val(meta), [bam] ]
    contigs         // channel: [ val(meta), [ bam ] ]

    main:

    ch_versions = Channel.empty()

   //BBMAP_COV ( fastp_reads, contigs)

    SEQKIT_TAB(contigs)

    //FILTER_CONTIGS(SEQKIT_TAB.out.contigs_tsv)

    //pitype_input = FILTER_CONTIGS.out.high_cov_contigs
        // .splitCsv(header: ['id', 'contig', 'length', 'coverage', 'sequence'], skip: 1, sep: '\t' )
        // .map{ row -> [[id: row.id, single_end: false], row.contig, row.length, row.coverage, row.sequence]}

    //PITYPE_WEB(pitype_input)

    //edirect_input = PITYPE_WEB.out.ref_pitype
        // .splitCsv(header: ['id', 'contig', 'genotype', 'reference'], skip: 1)
        // .map { row -> [[id: row.id, single_end: false], row.reference]}

    //EDIRECT_DOWNLOAD_REF(edirect_input)

    //BOWTIE2_BUILD(EDIRECT_DOWNLOAD_REF.out.pitype_reference)

    //fastp_reads
        // .join(EDIRECT_DOWNLOAD_REF.out.pitype_reference, by: [0], remainder: true)
        // .join(BOWTIE2_BUILD.out.index, by: [0], remainder: true)
        // .set { ch_align_input }

    //BOWTIE2_ALIGN(
        //     ch_align_input,
        //     params.save_unaligned,
        //     true
        // )

    //SAMTOOLS_SORT ( BOWTIE2_ALIGN.out.bam )
    //SAMTOOLS_INDEX ( SAMTOOLS_SORT.out.bam )
    
    //SAMTOOLS_SORT.out.bam
        // .join(SAMTOOLS_INDEX.out.bai, by: [0], remainder: true)
        // .join(SAMTOOLS_INDEX.out.csi, by: [0], remainder: true)
        // .map {
        //     meta, bam, bai, csi ->
        //         if (bai) {
        //             [ meta, bam, bai ]
        //         } else {
        //             [ meta, bam, csi ]
        //         }
        // }
        // .set { ch_bam_bai }

    //SAMTOOLS_STATS ( ch_bam_bai, EDIRECT_DOWNLOAD_REF.out.pitype_reference )
    //SAMTOOLS_FLAGSTAT ( ch_bam_bai )
    //SAMTOOLS_IDXSTATS ( ch_bam_bai )

    //SAMTOOLS_CONSENSUS ( SAMTOOLS_SORT.out.bam )
    //IVAR_CONSENSUS ( SAMTOOLS_SORT.out.bam, EDIRECT_DOWNLOAD_REF.out.pitype_reference, true )
    //SEQKIT_TAB_2 ( SAMTOOLS_CONSENSUS.out.consensus )

    //FILTER_CONTIGS_2 ( SEQKIT_TAB_2.out.contigs_tsv )

    // pitype_input_2 = FILTER_CONTIGS_2.out.high_cov_contigs
    //     .splitCsv(header: ['id', 'contig', 'length', 'coverage', 'sequence'], skip: 1, sep: '\t' )
    //     .map{ row -> [[id: row.id, single_end: false], row.contig, row.length, row.coverage, row.sequence]}

    //PITYPE_WEB_2 ( pitype_input_2 )


    // emit:
    // // TODO nf-core: edit emitted channels
    // bam      = SAMTOOLS_SORT.out.bam           // channel: [ val(meta), [ bam ] ]
    // bai      = SAMTOOLS_INDEX.out.bai          // channel: [ val(meta), [ bai ] ]
    // csi      = SAMTOOLS_INDEX.out.csi          // channel: [ val(meta), [ csi ] ]

    versions = ch_versions                     // channel: [ versions.yml ]
}

