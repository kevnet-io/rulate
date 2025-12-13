"""
Command-line interface for Rulate.

This provides commands for validating schemas, evaluating compatibility,
and managing catalogs.
"""

import json
import sys
from pathlib import Path

import click
import yaml

from rulate.engine import evaluate_item_against_catalog, evaluate_matrix, evaluate_pair
from rulate.engine.cluster_evaluator import find_clusters
from rulate.utils import load_catalog, load_cluster_ruleset, load_ruleset, load_schema


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """
    Rulate - Rule-based comparison engine CLI.

    Validate schemas, evaluate compatibility, and manage catalogs.
    """
    pass


# ============================================================================
# VALIDATE COMMANDS
# ============================================================================


@main.group()
def validate() -> None:
    """Validate schema, rule, and catalog files."""
    pass


@validate.command(name="schema")
@click.argument("file", type=click.Path(exists=True))
def validate_schema(file: str) -> None:
    """Validate a schema file."""
    try:
        schema = load_schema(file)
        click.secho(f"✓ Schema valid: {schema.name} v{schema.version}", fg="green")
        click.echo(f"  Dimensions: {len(schema.dimensions)}")

        for dim in schema.dimensions:
            required = " (required)" if dim.required else ""
            click.echo(f"    - {dim.name}: {dim.type.value}{required}")

        sys.exit(0)
    except Exception as e:
        click.secho("✗ Schema validation failed:", fg="red", err=True)
        click.echo(f"  {str(e)}", err=True)
        sys.exit(1)


@validate.command(name="rules")
@click.argument("file", type=click.Path(exists=True))
@click.option("--schema", type=click.Path(exists=True), help="Schema file to validate against")
def validate_rules(file: str, schema: str | None) -> None:
    """Validate a ruleset file."""
    try:
        ruleset = load_ruleset(file)
        click.secho(f"✓ RuleSet valid: {ruleset.name} v{ruleset.version}", fg="green")
        click.echo(f"  Schema: {ruleset.schema_ref}")
        click.echo(f"  Rules: {len(ruleset.rules)}")

        for rule in ruleset.rules:
            status = "enabled" if rule.enabled else "disabled"
            click.echo(f"    - {rule.name} ({rule.type.value}, {status})")

        if schema:
            schema_obj = load_schema(schema)
            if schema_obj.name != ruleset.schema_ref:
                click.secho(
                    f"⚠ Warning: RuleSet references schema '{ruleset.schema_ref}' "
                    f"but provided schema is '{schema_obj.name}'",
                    fg="yellow",
                )

        sys.exit(0)
    except Exception as e:
        click.secho("✗ RuleSet validation failed:", fg="red", err=True)
        click.echo(f"  {str(e)}", err=True)
        sys.exit(1)


@validate.command(name="catalog")
@click.argument("file", type=click.Path(exists=True))
@click.option("--schema", type=click.Path(exists=True), help="Schema file to validate against")
def validate_catalog(file: str, schema: str | None) -> None:
    """Validate a catalog file."""
    try:
        catalog = load_catalog(file)
        click.secho(f"✓ Catalog valid: {catalog.name}", fg="green")
        click.echo(f"  Schema: {catalog.schema_ref}")
        click.echo(f"  Items: {len(catalog.items)}")

        if schema:
            schema_obj = load_schema(schema)
            if schema_obj.name != catalog.schema_ref:
                click.secho(
                    f"⚠ Warning: Catalog references schema '{catalog.schema_ref}' "
                    f"but provided schema is '{schema_obj.name}'",
                    fg="yellow",
                )

            # Validate all items against schema
            click.echo("\n  Validating items against schema...")
            errors = 0
            for item in catalog.items:
                try:
                    schema_obj.validate_attributes(item.attributes)
                except Exception as e:
                    errors += 1
                    click.secho(f"    ✗ {item.id}: {str(e)}", fg="red")

            if errors == 0:
                click.secho(f"    ✓ All {len(catalog.items)} items valid", fg="green")
            else:
                click.secho(f"    {errors} items failed validation", fg="red")
                sys.exit(1)

        sys.exit(0)
    except Exception as e:
        click.secho("✗ Catalog validation failed:", fg="red", err=True)
        click.echo(f"  {str(e)}", err=True)
        sys.exit(1)


# ============================================================================
# EVALUATE COMMANDS
# ============================================================================


@main.group()
def evaluate() -> None:
    """Evaluate compatibility between items."""
    pass


@evaluate.command(name="pair")
@click.argument("item1_id")
@click.argument("item2_id")
@click.option("--catalog", "-c", required=True, type=click.Path(exists=True), help="Catalog file")
@click.option("--rules", "-r", required=True, type=click.Path(exists=True), help="Rules file")
@click.option("--schema", "-s", type=click.Path(exists=True), help="Schema file")
@click.option("--format", type=click.Choice(["summary", "json", "yaml"]), default="summary")
def evaluate_pair_cmd(
    item1_id: str, item2_id: str, catalog: str, rules: str, schema: str | None, format: str
) -> None:
    """Evaluate compatibility between two items."""
    try:
        # Load files
        catalog_obj = load_catalog(catalog)
        ruleset = load_ruleset(rules)
        schema_obj = load_schema(schema) if schema else None

        # Get items
        item1 = catalog_obj.get_item(item1_id)
        item2 = catalog_obj.get_item(item2_id)

        if not item1:
            click.secho(f"✗ Item '{item1_id}' not found in catalog", fg="red", err=True)
            sys.exit(1)
        if not item2:
            click.secho(f"✗ Item '{item2_id}' not found in catalog", fg="red", err=True)
            sys.exit(1)

        # Evaluate
        result = evaluate_pair(item1, item2, ruleset, schema_obj)

        # Output
        if format == "json":
            click.echo(json.dumps(result.model_dump(mode="python"), indent=2, default=str))
        elif format == "yaml":
            click.echo(yaml.dump(result.model_dump(mode="python"), default_flow_style=False))
        else:
            # Summary format
            status_color = "green" if result.compatible else "red"
            status_symbol = "✓" if result.compatible else "✗"
            click.secho(
                f"\n{status_symbol} {item1.name} + {item2.name}", fg=status_color, bold=True
            )
            click.echo(f"Compatible: {result.compatible}\n")

            click.echo("Rules evaluated:")
            for rule_eval in result.rules_evaluated:
                symbol = "✓" if rule_eval.passed else "✗"
                color = "green" if rule_eval.passed else "red"
                click.secho(f"  {symbol} {rule_eval.rule_name}", fg=color)
                click.echo(f"     {rule_eval.reason}")

        sys.exit(0 if result.compatible else 1)

    except Exception as e:
        click.secho("✗ Evaluation failed:", fg="red", err=True)
        click.echo(f"  {str(e)}", err=True)
        sys.exit(1)


@evaluate.command(name="matrix")
@click.option("--catalog", "-c", required=True, type=click.Path(exists=True), help="Catalog file")
@click.option("--rules", "-r", required=True, type=click.Path(exists=True), help="Rules file")
@click.option("--schema", "-s", type=click.Path(exists=True), help="Schema file")
@click.option("--format", type=click.Choice(["summary", "json", "yaml", "csv"]), default="summary")
@click.option("--output", "-o", type=click.Path(), help="Output file (default: stdout)")
def evaluate_matrix_cmd(
    catalog: str, rules: str, schema: str | None, format: str, output: str | None
) -> None:
    """Generate compatibility matrix for all items in a catalog."""
    try:
        # Load files
        catalog_obj = load_catalog(catalog)
        ruleset = load_ruleset(rules)
        schema_obj = load_schema(schema) if schema else None

        # Evaluate
        progress_length = len(catalog_obj.items) * (len(catalog_obj.items) - 1) // 2
        with click.progressbar(length=progress_length, label="Evaluating pairs") as bar:
            matrix = evaluate_matrix(catalog_obj, ruleset, schema_obj)
            bar.update(progress_length)

        # Prepare output
        if format == "json":
            output_text = json.dumps(matrix.model_dump(mode="python"), indent=2, default=str)
        elif format == "yaml":
            output_text = yaml.dump(matrix.model_dump(mode="python"), default_flow_style=False)
        elif format == "csv":
            # Generate CSV matrix
            from io import StringIO

            csv_buffer = StringIO()

            # Get all item IDs
            item_ids = [item.id for item in catalog_obj.items]

            # Write header
            csv_buffer.write("," + ",".join(item_ids) + "\n")

            # Write rows
            for item1_id in item_ids:
                row = [item1_id]
                for item2_id in item_ids:
                    if item1_id == item2_id:
                        row.append("1")
                    else:
                        result = matrix.get_result(item1_id, item2_id)
                        row.append("1" if result and result.compatible else "0")
                csv_buffer.write(",".join(row) + "\n")

            output_text = csv_buffer.getvalue()
        else:
            # Summary format
            stats = matrix.get_summary_stats()
            output_lines = []
            output_lines.append(f"\nCompatibility Matrix: {catalog_obj.name}")
            output_lines.append(f"Total comparisons: {stats['total_comparisons']}")
            output_lines.append(f"Compatible pairs: {stats['compatible_pairs']}")
            output_lines.append(f"Incompatible pairs: {stats['incompatible_pairs']}")
            output_lines.append(f"Compatibility rate: {stats['compatibility_rate']:.1%}\n")

            # Show sample compatible pairs
            compatible = matrix.get_compatible_pairs()[:5]
            if compatible:
                output_lines.append("Sample compatible pairs:")
                for result in compatible:
                    item1 = catalog_obj.get_item(result.item1_id)
                    item2 = catalog_obj.get_item(result.item2_id)
                    if item1 and item2:
                        output_lines.append(f"  ✓ {item1.name} + {item2.name}")

            output_text = "\n".join(output_lines)

        # Write output
        if output:
            Path(output).write_text(output_text)
            click.secho(f"✓ Matrix saved to {output}", fg="green")
        else:
            click.echo(output_text)

        sys.exit(0)

    except Exception as e:
        click.secho("✗ Matrix evaluation failed:", fg="red", err=True)
        click.echo(f"  {str(e)}", err=True)
        sys.exit(1)


@evaluate.command(name="item")
@click.argument("item_id")
@click.option("--catalog", "-c", required=True, type=click.Path(exists=True), help="Catalog file")
@click.option("--rules", "-r", required=True, type=click.Path(exists=True), help="Rules file")
@click.option("--schema", "-s", type=click.Path(exists=True), help="Schema file")
@click.option("--format", type=click.Choice(["summary", "json", "yaml"]), default="summary")
def evaluate_item_cmd(
    item_id: str, catalog: str, rules: str, schema: str | None, format: str
) -> None:
    """Find all items compatible with a specific item."""
    try:
        # Load files
        catalog_obj = load_catalog(catalog)
        ruleset = load_ruleset(rules)
        schema_obj = load_schema(schema) if schema else None

        # Get item
        item = catalog_obj.get_item(item_id)
        if not item:
            click.secho(f"✗ Item '{item_id}' not found in catalog", fg="red", err=True)
            sys.exit(1)

        # Evaluate
        results = evaluate_item_against_catalog(item, catalog_obj, ruleset, schema_obj)

        # Output
        if format == "json":
            click.echo(
                json.dumps([r.model_dump(mode="python") for r in results], indent=2, default=str)
            )
        elif format == "yaml":
            click.echo(
                yaml.dump([r.model_dump(mode="python") for r in results], default_flow_style=False)
            )
        else:
            # Summary format
            compatible = [r for r in results if r.compatible]
            incompatible = [r for r in results if not r.compatible]

            click.secho(f"\nCompatibility for: {item.name}", bold=True)
            click.secho(f"✓ Compatible: {len(compatible)}", fg="green")
            click.secho(f"✗ Incompatible: {len(incompatible)}", fg="red")

            if compatible:
                click.echo("\nCompatible items:")
                for result in compatible:
                    other_item = catalog_obj.get_item(result.item2_id)
                    if other_item:
                        click.secho(f"  ✓ {other_item.name}", fg="green")

            if incompatible and len(incompatible) <= 10:
                click.echo("\nIncompatible items:")
                for result in incompatible:
                    other_item = catalog_obj.get_item(result.item2_id)
                    if other_item:
                        click.secho(f"  ✗ {other_item.name}", fg="red")

        sys.exit(0)

    except Exception as e:
        click.secho("✗ Evaluation failed:", fg="red", err=True)
        click.echo(f"  {str(e)}", err=True)
        sys.exit(1)


@evaluate.command(name="clusters")
@click.option("--catalog", "-c", required=True, type=click.Path(exists=True), help="Catalog file")
@click.option(
    "--rules", "-r", required=True, type=click.Path(exists=True), help="Pairwise rules file"
)
@click.option(
    "--cluster-rules", "-cr", required=True, type=click.Path(exists=True), help="Cluster rules file"
)
@click.option("--schema", "-s", type=click.Path(exists=True), help="Schema file")
@click.option("--min-size", default=2, type=int, help="Minimum cluster size (default: 2)")
@click.option("--max-clusters", type=int, help="Maximum number of clusters to return")
@click.option("--format", type=click.Choice(["summary", "json", "yaml"]), default="summary")
@click.option("--output", "-o", type=click.Path(), help="Output file (default: stdout)")
def evaluate_clusters_cmd(
    catalog: str,
    rules: str,
    cluster_rules: str,
    schema: str | None,
    min_size: int,
    max_clusters: int | None,
    format: str,
    output: str | None,
) -> None:
    """Find all compatible clusters (sets of items) in a catalog."""
    try:
        # Load files
        catalog_obj = load_catalog(catalog)
        ruleset = load_ruleset(rules)
        cluster_ruleset = load_cluster_ruleset(cluster_rules)
        schema_obj = load_schema(schema) if schema else None

        # Find clusters
        click.echo("Finding clusters...")
        analysis = find_clusters(
            catalog_obj,
            ruleset,
            cluster_ruleset,
            schema_obj,
            min_cluster_size=min_size,
            max_clusters=max_clusters,
        )

        # Prepare output
        if format == "json":
            output_text = json.dumps(analysis.model_dump(mode="python"), indent=2, default=str)
        elif format == "yaml":
            output_text = yaml.dump(analysis.model_dump(mode="python"), default_flow_style=False)
        else:
            # Summary format
            output_lines = []
            output_lines.append(f"\nCluster Analysis: {catalog_obj.name} × {cluster_ruleset.name}")
            output_lines.append("=" * 70)
            output_lines.append(f"Found {analysis.total_clusters} cluster(s)")

            if analysis.total_clusters > 0:
                output_lines.append(
                    f"Cluster sizes: {analysis.min_cluster_size} - {analysis.max_cluster_size}"
                )
                output_lines.append(f"Average cluster size: {analysis.avg_cluster_size:.1f}")
                output_lines.append(
                    f"Items in clusters: {analysis.total_items_covered}/{len(catalog_obj.items)} ({analysis.total_items_covered/len(catalog_obj.items)*100:.1f}%)"
                )
                output_lines.append(f"Relationships: {len(analysis.relationships)}")
                output_lines.append("")

                # Show maximum clusters
                maximum_clusters = analysis.get_maximum_clusters()
                if maximum_clusters:
                    output_lines.append(
                        f"Maximum Clusters ({len(maximum_clusters)} @ {maximum_clusters[0].size} items):"
                    )
                    for i, cluster in enumerate(maximum_clusters[:3], 1):
                        output_lines.append(f"\n  Cluster #{i} (ID: {cluster.id[:8]}...)")
                        output_lines.append(f"  Items: {cluster.item_ids}")

                        # Get item names
                        item_names = []
                        for item_id in cluster.item_ids[:5]:
                            item = catalog_obj.get_item(item_id)
                            if item:
                                item_names.append(item.name)
                        if len(cluster.item_ids) > 5:
                            item_names.append(f"... +{len(cluster.item_ids) - 5} more")
                        output_lines.append(f"  Names: {', '.join(item_names)}")

                        # Show rule evaluations
                        passed = len([r for r in cluster.rule_evaluations if r.passed])
                        total = len(cluster.rule_evaluations)
                        output_lines.append(f"  Rules: {passed}/{total} passed")

                        # Show relationships
                        rels = analysis.get_relationships_for_cluster(cluster.id)
                        if rels:
                            rel_summary: dict[str, int] = {}
                            for rel in rels:
                                rel_type = rel.relationship_type
                                rel_summary[rel_type] = rel_summary.get(rel_type, 0) + 1
                            rel_text = ", ".join(
                                f"{count} {rel_type}" for rel_type, count in rel_summary.items()
                            )
                            output_lines.append(f"  Relationships: {rel_text}")

                    if len(maximum_clusters) > 3:
                        output_lines.append(
                            f"\n  ... and {len(maximum_clusters) - 3} more maximum clusters"
                        )

                # Show some smaller clusters
                other_clusters = [c for c in analysis.clusters if not c.is_maximum]
                if other_clusters:
                    output_lines.append(f"\n\nOther Clusters ({len(other_clusters)}):")
                    for cluster in other_clusters[:5]:
                        output_lines.append(
                            f"  - {cluster.size} items: {cluster.item_ids[:3]}{'...' if len(cluster.item_ids) > 3 else ''}"
                        )
                    if len(other_clusters) > 5:
                        output_lines.append(f"  ... and {len(other_clusters) - 5} more")

            output_lines.append("")
            output_text = "\n".join(output_lines)

        # Write output
        if output:
            Path(output).write_text(output_text)
            click.secho(f"✓ Cluster analysis saved to {output}", fg="green")
        else:
            click.echo(output_text)

        sys.exit(0)

    except Exception as e:
        click.secho("✗ Cluster evaluation failed:", fg="red", err=True)
        click.echo(f"  {str(e)}", err=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)


# ============================================================================
# SHOW COMMANDS
# ============================================================================


@main.group()
def show() -> None:
    """Display information about schemas, catalogs, and items."""
    pass


@show.command(name="schema")
@click.argument("file", type=click.Path(exists=True))
@click.option("--format", type=click.Choice(["summary", "json", "yaml"]), default="summary")
def show_schema(file: str, format: str) -> None:
    """Display schema information."""
    try:
        schema = load_schema(file)

        if format == "json":
            click.echo(json.dumps(schema.model_dump(mode="python"), indent=2))
        elif format == "yaml":
            click.echo(yaml.dump(schema.model_dump(mode="python"), default_flow_style=False))
        else:
            click.secho(f"\nSchema: {schema.name} v{schema.version}", bold=True)
            if schema.description:
                click.echo(f"{schema.description}\n")

            click.echo(f"Dimensions ({len(schema.dimensions)}):")
            for dim in schema.dimensions:
                required = " *" if dim.required else ""
                click.echo(f"  {dim.name}{required}: {dim.type.value}")
                if dim.description:
                    click.echo(f"    {dim.description}")
                if dim.type.value == "enum" and dim.values:
                    click.echo(f"    Values: {', '.join(dim.values)}")
                if dim.min is not None or dim.max is not None:
                    range_str = f"Range: {dim.min or '-∞'} to {dim.max or '∞'}"
                    click.echo(f"    {range_str}")

        sys.exit(0)
    except Exception as e:
        click.secho("✗ Failed to load schema:", fg="red", err=True)
        click.echo(f"  {str(e)}", err=True)
        sys.exit(1)


@show.command(name="catalog")
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--format", type=click.Choice(["summary", "json", "yaml", "table"]), default="summary"
)
def show_catalog(file: str, format: str) -> None:
    """Display catalog information."""
    try:
        catalog = load_catalog(file)

        if format == "json":
            click.echo(json.dumps(catalog.model_dump(mode="python"), indent=2, default=str))
        elif format == "yaml":
            click.echo(yaml.dump(catalog.model_dump(mode="python"), default_flow_style=False))
        elif format == "table":
            # Simple table format
            click.secho(f"\nCatalog: {catalog.name}", bold=True)
            click.echo(f"Schema: {catalog.schema_ref}")
            click.echo(f"\nItems ({len(catalog.items)}):")
            click.echo("-" * 80)
            click.echo(f"{'ID':<20} {'Name':<30} {'Attributes':<30}")
            click.echo("-" * 80)
            for item in catalog.items:
                attrs = ", ".join(f"{k}={v}" for k, v in list(item.attributes.items())[:3])
                if len(item.attributes) > 3:
                    attrs += "..."
                click.echo(f"{item.id:<20} {item.name:<30} {attrs:<30}")
        else:
            # Summary
            click.secho(f"\nCatalog: {catalog.name}", bold=True)
            if catalog.description:
                click.echo(f"{catalog.description}")
            click.echo(f"Schema: {catalog.schema_ref}")
            click.echo(f"Items: {len(catalog.items)}\n")

            # Sample items
            for item in catalog.items[:10]:
                click.echo(f"  - {item.name} ({item.id})")
            if len(catalog.items) > 10:
                click.echo(f"  ... and {len(catalog.items) - 10} more")

        sys.exit(0)
    except Exception as e:
        click.secho("✗ Failed to load catalog:", fg="red", err=True)
        click.echo(f"  {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
