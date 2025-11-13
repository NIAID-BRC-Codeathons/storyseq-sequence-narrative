# Test fastas

## Poxvirus an outlier poxvirus, a gene of unknown function, and a well classified one
   * genome: [genome/poxvirus.NY_014.fna](genome/poxvirus.NY_014.fna)
   * genes:
      * hypothetical protein (unknown function)
        * [gene/prot/poxvirus.hypothetical_protein.NY_014-012.faa](gene/prot/poxvirus.hypothetical_protein.NY_014-012.faa)
        * [gene/nuc/poxvirus.hypothetical_protein.NY_014-012.fna](gene/nuc/poxvirus.hypothetical_protein.NY_014-012.fna)
      * entry/fusion complex component (known viral function)
        * [gene/prot/poxvirus.entry_fusion_component.NY_014-079.faa](gene/prot/poxvirus.entry_fusion_component.NY_014-079.faa)
        * [gene/nuc/poxvirus.entry_fusion_component.NY_014-079.fna](gene/nuc/poxvirus.entry_fusion_component.NY_014-079.fna)

## Bacterial AMR genes

From BV-BRC AMR Workshop: https://www.bv-brc.org/workspace/ARWattam@patricbrc.org/BV-BRC%20Workshop/AMR_Workshop/Streptococcus/8_BLAST
  * genes identified as being important targets by beta lactam antibiotics in Streptococcus pneumoniae
    * PBP1a 
      * [gene/prot/streptococcus_pneumoniae.PBP1a.faa](gene/prot/streptococcus_pneumoniae.PBP1a.faa) 
      * [gene/nuc/streptococcus_pneumoniae.PBP1a.fna](gene/nuc/streptococcus_pneumoniae.PBP1a.fna)
  * genes identified as being important targets by tetracycline resistance in Streptococcus pneumoniae
    * TetM
      * [gene/prot/streptococcus_pneumoniae.TetM.faa](gene/prot/streptococcus_pneumoniae.TetM.faa)
      * [gene/nuc/streptococcus_pneumoniae.TetM.fna](gene/nuc/streptococcus_pneumoniae.TetM.fna)

## Random Genes 

* FCGR2A 
  * Human
    * [gene/prot/human.fcgr2a.faa](gene/prot/human.fcgr2a.faa)
  * Mouse homolog
    * [gene/prot/mouse.fcgr2a.faa](gene/prot/mouse.fcgr2a.faa)
* M002 IL12 construct - a mixture of HSV1, HepB, mouse IL12 and other construct sequences
  These sequences contain DNA from a mixture of organisms. A naive megablast will identify the HSV1 sequences at the end, but the mouse IL12 sequence will be lost far down the results. Ideally, one realizes there's a coverage gap and follows up with additional blasts excluding Herpeseviridae to determine the full complement of genes in the sequence. 
  * just the construct: [gene/nuc/m002_il12_cassette.fna](gene/nuc/m002_il12_cassette.fna)
  * including adjacent HSV1 RL2 CDS [gene/nuc/m002_il12_cassette_and_RL2.fna](gene/nuc/m002_il12_cassette_and_RL2.fna)
