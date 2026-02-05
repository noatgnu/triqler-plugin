# Triqler Protein Quantification


## Installation

**[⬇️ Click here to install in Cauldron](http://localhost:50060/install?repo=https%3A%2F%2Fgithub.com%2Fnoatgnu%2Ftriqler-plugin)** _(requires Cauldron to be running)_

> **Repository**: `https://github.com/noatgnu/triqler-plugin`

**Manual installation:**

1. Open Cauldron
2. Go to **Plugins** → **Install from Repository**
3. Paste: `https://github.com/noatgnu/triqler-plugin`
4. Click **Install**

**ID**: `triqler`  
**Version**: 1.0.2  
**Category**: statistics  
**Author**: CauldronGO Team

## Description

Protein quantification with integrated error propagation using Triqler. Propagates uncertainty from MS1 features through peptide to protein level using a probabilistic graphical model, producing posterior probabilities for differential expression. Based on: The & Käll (2019) Mol Cell Proteomics 18(3):561-570. Repository: https://github.com/statisticalbiotechnology/triqler

## Runtime

- **Environments**: `python`

- **Entrypoint**: `triqler_runner.py`

## Inputs

| Name | Label | Type | Required | Default | Visibility |
|------|-------|------|----------|---------|------------|
| `input_format` | Input Format | select (triqler, diann, maxquant) | Yes | triqler | Always visible |
| `input_file` | Input File | file | Yes | - | Always visible |
| `file_list_file` | Run Mapping File | file | No | - | Conditional |
| `fold_change_eval` | Log2 Fold Change Threshold | number (min: 0, max: 10, step: 0) | No | 1 | Always visible |
| `decoy_pattern` | Decoy Protein Prefix | text | No | decoy_ | Always visible |
| `min_samples` | Minimum Samples | number (min: 1, max: 20, step: 1) | No | 2 | Always visible |
| `missing_value_prior` | Missing Value Prior | select (default, DIA) | No | default | Always visible |
| `num_threads` | Number of Threads | number (min: 0, max: 64, step: 1) | No | 0 | Always visible |
| `use_ttest` | Use T-Test | boolean | No | false | Always visible |
| `write_spectrum_quants` | Write Spectrum Quantifications | boolean | No | false | Always visible |
| `write_protein_posteriors` | Write Protein Posteriors | boolean | No | false | Always visible |
| `write_group_posteriors` | Write Group Posteriors | boolean | No | false | Always visible |
| `write_fold_change_posteriors` | Write Fold Change Posteriors | boolean | No | false | Always visible |

### Input Details

#### Input Format (`input_format`)

Format of the input file. Select 'triqler' for pre-formatted files, 'diann' for DIA-NN report files, or 'maxquant' for MaxQuant evidence.txt

- **Options**: `triqler`, `diann`, `maxquant`

#### Input File (`input_file`)

For triqler format: PSM file with columns (run, condition, charge, searchScore, intensity, peptide, proteins). For DIA-NN: report.tsv or report.parquet. For MaxQuant: evidence.txt


#### Run Mapping File (`file_list_file`)

Required for DIA-NN/MaxQuant: Tab-separated file (NO HEADER) mapping run names to conditions. For DIA-NN: run names must match the 'Run' column. For MaxQuant: must match 'Raw file' column without path. Columns: run, condition, [sample], [fraction]


#### Log2 Fold Change Threshold (`fold_change_eval`)

Log2 fold change evaluation threshold for differential expression


#### Decoy Protein Prefix (`decoy_pattern`)

Prefix used to identify decoy proteins in reversed database search

- **Placeholder**: `decoy_`

#### Minimum Samples (`min_samples`)

Minimum number of peptide quantifications required per protein


#### Missing Value Prior (`missing_value_prior`)

Distribution fitting method for missing values. Use DIA for DIA data.

- **Options**: `default`, `DIA`

#### Number of Threads (`num_threads`)

Number of CPU threads to use (0 = use all available cores)


#### Use T-Test (`use_ttest`)

Use t-test instead of Bayesian posterior probabilities for differential expression


#### Write Spectrum Quantifications (`write_spectrum_quants`)

Output consensus spectrum quantification data


#### Write Protein Posteriors (`write_protein_posteriors`)

Export protein posterior distributions to a separate file


#### Write Group Posteriors (`write_group_posteriors`)

Export treatment group posterior distributions to a separate file


#### Write Fold Change Posteriors (`write_fold_change_posteriors`)

Export fold change posterior distributions to a separate file


## Outputs

| Name | File | Type | Format | Description |
|------|------|------|--------|-------------|
| `protein_results` | `proteins.tsv` | data | tsv | Protein-level quantification results with q-values, posterior error probabilities, and fold change estimates |
| `triqler_input` | `triqler_input.tsv` | data | tsv | Converted triqler input file (only generated when using DIA-NN or MaxQuant format) |
| `spectrum_quants` | `spectrum_quants.tsv` | data | tsv | Consensus spectrum quantification data |
| `protein_posteriors` | `protein_posteriors.tsv` | data | tsv | Protein posterior distributions |
| `group_posteriors` | `group_posteriors.tsv` | data | tsv | Treatment group posterior distributions |
| `fold_change_posteriors` | `fold_change_posteriors.tsv` | data | tsv | Fold change posterior distributions |

## Requirements

- **Python Version**: >=3.10

### Python Dependencies (External File)

Dependencies are defined in: `requirements.txt`

- `triqler>=0.6.0`
- `click>=8.0.0`
- `pyarrow>=10.0.0`

> **Note**: When you create a custom environment for this plugin, these dependencies will be automatically installed.

## Usage

### Via UI

1. Navigate to **statistics** → **Triqler Protein Quantification**
2. Fill in the required inputs
3. Click **Run Analysis**

### Via Plugin System

```typescript
const jobId = await pluginService.executePlugin('triqler', {
  // Add parameters here
});
```
