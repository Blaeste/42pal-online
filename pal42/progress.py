"""The progress of a student: what the history and the grademe say.

history.json lists the finished exams; grades.json lists each grademe (the
subject, its themes, OK or KO, in an exam or in practice). From them: each
exam with its best grade, the themes that fail the most, and one line that
sums it all up. An exam where the cheat menu was used does not count. Like
the rest of the core, this module never prints.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class ExamRow:
	"""An exam of the history: how many times it was taken, passed, and the best grade."""
	exam: str
	title: str
	tries: int
	passed: int
	best: float

@dataclass(frozen=True)
class ThemeRow:
	"""A theme: how many grademe were made on its subjects, and how many passed."""
	theme: str
	tries: int
	oks: int

	@property
	def rate(self):
		return self.oks / self.tries if self.tries else 0

def _fair(history):
	"""The finished exams where the cheat menu was not used."""
	return [entry for entry in history if not entry.get("cheat")]

def exam_rows(history):
	"""Each exam taken, in the order of its first time, with its best grade."""
	rows = {}
	for entry in _fair(history):
		row = rows.get(entry["exam"])
		grade = round(entry.get("grade", 0), 2)
		passed = int(entry.get("end") == "passed")
		if row is None:
			rows[entry["exam"]] = ExamRow(entry["exam"], entry.get("title", entry["exam"]), 1, passed, grade)
		else:
			rows[entry["exam"]] = ExamRow(row.exam, row.title, row.tries + 1, row.passed + passed, max(row.best, grade))
	return list(rows.values())

def theme_rows(grades):
	"""Each theme met in a grademe, with its tries and its OK."""
	counts = {}
	for entry in grades:
		for theme in entry.get("themes", ()):
			tries, oks = counts.get(theme, (0, 0))
			counts[theme] = (tries + 1, oks + bool(entry.get("passed")))
	return [ThemeRow(theme, tries, oks) for theme, (tries, oks) in counts.items()]

def weak_themes(grades, limit=5):
	"""The themes that fail the most, at most `limit`: the lowest rate of OK first.

	Among themes with the same rate, the one tried the most comes first. A
	theme whose every grademe passed is not weak.
	"""
	rows = [row for row in theme_rows(grades) if row.oks < row.tries]
	return sorted(rows, key=lambda row: (row.rate, -row.tries, row.theme))[:limit]

def summary(history, grades):
	"""One line: the exams taken, the grademe made, how many passed, the best grade."""
	if not grades and not history:
		return "No grademe yet"
	fair = _fair(history)
	oks = sum(1 for entry in grades if entry.get("passed"))
	rate = f" ({round(100 * oks / len(grades))}%)" if grades else ""
	parts = [f"{len(fair)} exam{'s' if len(fair) != 1 else ''}"] if fair else []
	parts += [f"{len(grades)} grademe", f"{oks} OK{rate}"]
	if fair:
		best = max(fair, key=lambda entry: entry.get("grade", 0))
		parts.append(f"best {round(best.get('grade', 0), 2):g}/100, {best.get('title', best['exam'])}")
	return " · ".join(parts)
