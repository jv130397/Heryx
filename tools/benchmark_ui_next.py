"""Reproducible local measurements for the Genomic Nexus prototype."""

import json
import resource
import time
from statistics import median

from PySide6.QtGui import QGuiApplication

from rarepedigree.domain import GenderIdentity, Individual, Parentage, PedigreeProject
from rarepedigree.layout import PedigreeLayoutEngine
from rarepedigree.ui_next import NexusController
from rarepedigree.ui_next.app import create_engine


def project_with_size(size: int) -> PedigreeProject:
    project = PedigreeProject(title=f"Benchmark {size}")
    for index in range(size):
        gender = GenderIdentity.MAN if index % 2 == 0 else GenderIdentity.WOMAN
        project.individuals.append(Individual(label=f"P-{index + 1}", gender_identity=gender))
    first = max(2, size // 3)
    second = max(first + 1, size * 2 // 3)
    for index in range(first, second):
        project.parentages.append(
            Parentage(parent_id=project.individuals[index % first].id,
                      child_id=project.individuals[index].id)
        )
    for index in range(second, size):
        project.parentages.append(
            Parentage(parent_id=project.individuals[first + (index % (second-first))].id,
                      child_id=project.individuals[index].id)
        )
    positions = PedigreeLayoutEngine().compute(project)
    for person in project.individuals:
        person.layout.x, person.layout.y = positions[person.id]
    return project


def measure(size: int, app: QGuiApplication) -> dict:
    project = project_with_size(size)
    started = time.perf_counter()
    controller = NexusController(project)
    controller_ms = (time.perf_counter() - started) * 1000
    started = time.perf_counter()
    engine = create_engine(controller)
    app.processEvents()
    qml_ms = (time.perf_counter() - started) * 1000
    samples = []
    for person in project.individuals[: min(size, 30)]:
        started = time.perf_counter()
        controller.selectPerson(str(person.id))
        samples.append((time.perf_counter() - started) * 1000)
    roots = len(engine.rootObjects())
    del engine
    app.processEvents()
    return {
        "individuals": size,
        "controller_load_ms": round(controller_ms, 3),
        "qml_start_ms": round(qml_ms, 3),
        "median_selection_ms": round(median(samples), 4),
        "root_objects": roots,
        "process_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


def main() -> None:
    app = QGuiApplication.instance() or QGuiApplication([])
    results = [measure(size, app) for size in (10, 30, 100)]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
