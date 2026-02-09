"""Wrapper script for running Triqler protein quantification analysis."""

import os
import sys
import shutil
import subprocess
import glob
import csv
from io import StringIO
from typing import Optional

import click


def convert_diann_to_triqler(
    input_file: str,
    file_list_file: str,
    output_file: str,
) -> None:
    """Convert DIA-NN output to triqler input format."""
    cmd = [
        sys.executable, "-m", "triqler.convert.diann",
        input_file,
        "--file_list_file", file_list_file,
        "--out_file", output_file,
    ]
    print(f"Converting DIA-NN format: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"DIA-NN conversion failed: {result.stderr}")


def convert_maxquant_to_triqler(
    input_file: str,
    file_list_file: str,
    output_file: str,
) -> None:
    """Convert MaxQuant evidence.txt to triqler input format."""
    cmd = [
        sys.executable, "-m", "triqler.convert.maxquant",
        input_file,
        "--file_list_file", file_list_file,
        "--out_file", output_file,
    ]
    print(f"Converting MaxQuant format: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"MaxQuant conversion failed: {result.stderr}")


def export_condition_mapping(triqler_input_file: str, output_dir: str) -> None:
    """Reads Triqler input, extracts conditions, sorts them alphabetically, and writes a mapping file."""
    conditions = set()
    try:
        with open(triqler_input_file, 'r') as f:
            header = f.readline().strip().split('\t')
            # Determine condition column index
            try:
                # Try to find 'condition' column by name (case-insensitive)
                cond_idx = next(i for i, col in enumerate(header) if col.lower() == 'condition')
            except StopIteration:
                # Fallback to index 1 (standard Triqler format: run, condition, ...)
                cond_idx = 1
            
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) > cond_idx:
                    conditions.add(parts[cond_idx])
        
        sorted_conditions = sorted(list(conditions))
        
        map_file = os.path.join(output_dir, "condition_mapping.tsv")
        with open(map_file, 'w') as f:
            f.write("ID\tCondition\n")
            for idx, cond in enumerate(sorted_conditions, 1):
                f.write(f"{idx}\t{cond}\n")
        
        print(f"Condition mapping written to: {map_file}")
        print("Condition Mapping (Alphabetical):")
        for idx, cond in enumerate(sorted_conditions, 1):
            print(f"  {idx}: {cond}")
            
    except Exception as e:
        print(f"Warning: Could not extract condition mapping: {e}", file=sys.stderr)


def add_gene_names(output_dir: str, decoy_pattern: str) -> None:
    """Adds a gene name column to all protein results files in the output directory using uniprotparser."""
    try:
        from uniprotparser.betaparser import UniprotParser
    except ImportError:
        print("Warning: uniprotparser not installed. Skipping gene name annotation.", file=sys.stderr)
        return

    protein_files = glob.glob(os.path.join(output_dir, "proteins*.tsv"))
    if not protein_files:
        return

    accessions = set()
    for file_path in protein_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t")
                if not reader.fieldnames or "protein" not in reader.fieldnames:
                    continue
                for row in reader:
                    prot = row["protein"]
                    for acc in prot.split(";"):
                        if not acc.startswith(decoy_pattern):
                            accessions.add(acc)
        except Exception as e:
            print(f"Warning: Could not read {file_path} for accession extraction: {e}", file=sys.stderr)

    if not accessions:
        return

    print(f"Fetching gene names for {len(accessions)} proteins from UniProt...")
    parser = UniprotParser()
    mapping = {}
    
    try:
        # uniprotparser returns a generator of result chunks (TSV format)
        for result_chunk in parser.parse(ids=list(accessions), columns=["genes"]):
            f = StringIO(result_chunk)
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                # 'From' contains the original accession, 'Gene Names' contains names
                acc = row.get("From")
                gene = row.get("Gene Names", "")
                if acc and gene:
                    # Take the first gene name (usually the primary one)
                    mapping[acc] = str(gene).split(" ")[0]
    except Exception as e:
        print(f"Warning: UniProt mapping failed: {e}", file=sys.stderr)
        return

    # Update files with gene names
    for file_path in protein_files:
        try:
            temp_file = file_path + ".tmp"
            with open(file_path, "r", encoding="utf-8") as f_in, \
                 open(temp_file, "w", encoding="utf-8", newline="") as f_out:
                
                reader = csv.DictReader(f_in, delimiter="\t")
                fieldnames = list(reader.fieldnames) if reader.fieldnames else []
                
                if "protein" not in fieldnames:
                    continue
                
                prot_idx = fieldnames.index("protein")
                # Insert gene_name right after protein column
                new_fieldnames = fieldnames[:prot_idx+1] + ["gene_name"] + fieldnames[prot_idx+1:]
                
                writer = csv.DictWriter(f_out, fieldnames=new_fieldnames, delimiter="\t")
                writer.writeheader()
                
                for row in reader:
                    accs = row["protein"].split(";")
                    genes = [mapping.get(acc, "") for acc in accs]
                    # Filter out empty strings and join with semicolon
                    row["gene_name"] = ";".join(filter(None, genes))
                    writer.writerow(row)
            
            os.replace(temp_file, file_path)
        except Exception as e:
            print(f"Warning: Could not update {file_path} with gene names: {e}", file=sys.stderr)
    
    print("Gene name annotation complete.")


@click.command()
@click.option("--input_format", type=click.Choice(["triqler", "diann", "maxquant"]), default="triqler", help="Input file format")
@click.option("--input_file", required=True, help="Input file path")
@click.option("--file_list_file", default=None, help="Sample annotation file (required for DIA-NN/MaxQuant)")
@click.option("--output_dir", required=True, help="Output directory for results")
@click.option("--fold_change_eval", type=float, default=1.0, help="Log2 fold change threshold")
@click.option("--decoy_pattern", default="decoy_", help="Decoy protein prefix")
@click.option("--min_samples", type=int, default=2, help="Minimum peptide quantifications required")
@click.option("--missing_value_prior", default="default", help="Missing value prior (default or DIA)")
@click.option("--num_threads", type=int, default=0, help="Number of threads (0 = all cores)")
@click.option("--use_ttest", is_flag=True, default=False, help="Use t-test instead of posterior probabilities")
@click.option("--write_spectrum_quants", is_flag=True, default=False, help="Output spectrum quantifications")
@click.option("--write_protein_posteriors", is_flag=True, default=False, help="Export protein posteriors")
@click.option("--write_group_posteriors", is_flag=True, default=False, help="Export group posteriors")
@click.option("--write_fold_change_posteriors", is_flag=True, default=False, help="Export fold change posteriors")
def run_triqler(
    input_format: str,
    input_file: str,
    file_list_file: Optional[str],
    output_dir: str,
    fold_change_eval: float,
    decoy_pattern: str,
    min_samples: int,
    missing_value_prior: str,
    num_threads: int,
    use_ttest: bool,
    write_spectrum_quants: bool,
    write_protein_posteriors: bool,
    write_group_posteriors: bool,
    write_fold_change_posteriors: bool,
) -> None:
    """Run Triqler protein quantification with error propagation."""
    os.makedirs(output_dir, exist_ok=True)

    triqler_input_file = input_file

    if input_format in ("diann", "maxquant"):
        if not file_list_file:
            raise click.UsageError(
                f"--file_list_file is required when using {input_format} format. "
                "This file maps run names to experimental conditions."
            )

        triqler_input_file = os.path.join(output_dir, "triqler_input.tsv")

        if input_format == "diann":
            convert_diann_to_triqler(input_file, file_list_file, triqler_input_file)
        elif input_format == "maxquant":
            convert_maxquant_to_triqler(input_file, file_list_file, triqler_input_file)

        print(f"Converted input saved to: {triqler_input_file}")

    # Export mapping for clarity
    export_condition_mapping(triqler_input_file, output_dir)

    out_file = os.path.join(output_dir, "proteins.tsv")

    cmd = [
        sys.executable, "-m", "triqler",
        "--out_file", out_file,
        "--fold_change_eval", str(fold_change_eval),
        "--decoy_pattern", decoy_pattern,
        "--min_samples", str(min_samples),
    ]

    if missing_value_prior == "DIA":
        cmd.extend(["--missing_value_prior", "DIA"])

    if num_threads > 0:
        cmd.extend(["--num_threads", str(num_threads)])

    # Input file must come before boolean flags in some versions of Triqler
    cmd.append(triqler_input_file)

    if use_ttest:
        cmd.append("--ttest")

    if write_spectrum_quants:
        cmd.append("--write_spectrum_quants")

    if write_protein_posteriors:
        posteriors_path = os.path.join(output_dir, "protein_posteriors.tsv")
        cmd.extend(["--write_protein_posteriors", posteriors_path])

    if write_group_posteriors:
        group_path = os.path.join(output_dir, "group_posteriors.tsv")
        cmd.extend(["--write_group_posteriors", group_path])

    if write_fold_change_posteriors:
        fc_path = os.path.join(output_dir, "fold_change_posteriors.tsv")
        cmd.extend(["--write_fold_change_posteriors", fc_path])

    print(f"Running Triqler: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        sys.exit(result.returncode)

    if write_spectrum_quants:
        base_name = os.path.splitext(os.path.basename(triqler_input_file))[0]
        spectrum_file = f"{base_name}.spectrum_quants.tsv"
        if os.path.exists(spectrum_file):
            print(f"Moving spectrum quants to output directory: {spectrum_file}")
            shutil.move(spectrum_file, os.path.join(output_dir, "spectrum_quants.tsv"))
        else:
            print(f"Warning: Expected spectrum quants file {spectrum_file} not found.", file=sys.stderr)

    # Add gene names using UniProt
    add_gene_names(output_dir, decoy_pattern)

    print(f"Triqler analysis complete. Results written to: {output_dir}")


if __name__ == "__main__":
    run_triqler()
