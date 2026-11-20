"""./42pal check-catalog: is every exercise of the catalog graded right?

For each exercise, its reference solution (ref.c, or ref.py for Python) is
graded like a student's rendu on every variant (see pal42.reference). A
variant where it fails means that the oracle or the reference is wrong: the
command names it (exo#seed) with its trace.
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.console import Console
from rich.markup import escape
from rich.text import Text

from pal42.catalog import load_catalog
from pal42.reference import check_variant, reference_path, variants_to_check

def check_catalog(console=None, catalog=None, names=None):
	"""Check the exercises of `catalog` (all, or those `names`); print the result; return the exit code.

	0 when everything is right, 1 when something is wrong: a ref.c that fails
	a variant, a missing ref.c, an unknown name, or a folder the catalog had
	to skip.
	"""
	console = console or Console()
	catalog = catalog or load_catalog()
	ok = True
	for warning in catalog.warnings:
		console.print(f"[bold red]✗[/] {escape(warning)}")
		ok = False
	for name in names or ():
		if name not in catalog.exercises:
			console.print(f"[bold red]✗[/] Unknown exercise: {escape(name)}")
			return 1
	chosen = names or list(catalog.exercises)
	refs = {name: reference_path(catalog.exercises[name], catalog.folders[name]) for name in chosen}
	if refs and not any(ref.is_file() for ref in refs.values()):
		# The archive of a release leaves the reference solutions out.
		console.print("[bold red]✗[/] No reference solution here: check-catalog needs a git clone"
			" of 42pal (the archive of a release leaves them out).")
		return 1
	variants_checked = 0
	for name in sorted(chosen):
		ref = refs[name]
		if not ref.is_file():
			console.print(f"[bold red]✗[/] {escape(name)}: no {ref.name}")
			ok = False
			continue
		failures, total = _check_exercise(console, catalog.exercises[name], name, ref)
		variants_checked += total
		mark = "[bold red]✗[/]" if failures else "[bold green]✓[/]"
		console.print(f"{mark} {escape(name):16} {total - len(failures)}/{total} variants OK")
		for variant, result in failures:
			params = ", ".join(f"{key}={value}" for key, value in variant.params.items())
			console.print(f"  {escape(variant.id)} ({escape(params)})")
			# Text: the trace is shown as it is, with no rich markup read in it.
			console.print(Text(result.trace))
		ok = ok and not failures
	if ok:
		console.print(f"[bold green]Catalog OK[/]: {len(chosen)} exercises, "
			f"{variants_checked} variants")
	else:
		console.print("[bold red]Catalog KO[/]: see the errors above")
	return 0 if ok else 1

def _check_exercise(console, exo, name, ref):
	"""Grade ref.c on each variant to check; return the failures and the count.

	The variants are graded at the same time, one thread each, up to one per
	processor: the work is done by cc, the programs and valgrind, in their own
	processes. The failures come back in the order of the variants.
	"""
	variants = variants_to_check(exo)
	# A spinner while checking; rich shows it only in a real terminal.
	with console.status(f"Checking {name}…") as status:
		with ThreadPoolExecutor(max_workers=os.cpu_count() or 1) as pool:
			futures = [pool.submit(check_variant, variant, ref) for variant in variants]
			for done, _ in enumerate(as_completed(futures), start=1):
				status.update(f"Checking {name}… variant {done}/{len(variants)}")
	failures = [
		(variant, future.result()) for variant, future in zip(variants, futures)
		if not future.result().passed
	]
	return failures, len(variants)
