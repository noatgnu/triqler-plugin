"""Wrapper script for running Triqler protein quantification analysis."""

import os
import sys
import shutil
import subprocess
from typing import List, Optional

import click


@click.command()
@click.option("--input_file", required=True, help="Input PSM file (tab-separated)")
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
    input_file: str,
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

    out_file = os.path.join(output_dir, "proteins.tsv")

    cmd: List[str] = [
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

    cmd.append(input_file)

    print(f"Running Triqler: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if write_spectrum_quants:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        spectrum_file = f"{base_name}.spectrum_quants.tsv"
        if os.path.exists(spectrum_file):
            shutil.move(spectrum_file, os.path.join(output_dir, "spectrum_quants.tsv"))

    if result.returncode != 0:
        sys.exit(result.returncode)

    print(f"Triqler analysis complete. Results written to: {output_dir}")


if __name__ == "__main__":
    run_triqler()
