#!/usr/bin/env python3

import shutil
from pathlib import Path
from Pegasus.api import *

wf = Workflow("pegasus-simple")

# --- Sites ---

sc = SiteCatalog()

WORK_DIR = Path.cwd().resolve()

shared_scratch_dir = str(WORK_DIR / "scratch")
local_storage_dir = str(WORK_DIR / "outputs")

local = Site("local").add_directories(
    Directory(Directory.SHARED_SCRATCH, shared_scratch_dir).add_file_servers(
        FileServer("file://" + shared_scratch_dir, Operation.ALL)
    ),
    Directory(Directory.LOCAL_STORAGE, local_storage_dir).add_file_servers(
        FileServer("file://" + local_storage_dir, Operation.ALL)
    ),
)

condorpool_amd = (
    Site("condorpool", arch=Arch.X86_64)
    .add_pegasus_profile(style="condor")
    .add_pegasus_profile(auxillary_local="true")
    .add_condor_profile(universe="vanilla")
)

sc.add_sites(local, condorpool_amd)

sc.write()

# --- Transformations ---

task_a = Transformation(
    "task-a",
    site="condorpool",
    pfn=Path(shutil.which("pegasus-keg")).resolve(),
    is_stageable=True,
    arch=Arch.X86_64,
    os_type=OS.LINUX,
)

tc = TransformationCatalog().add_transformations(task_a).write()

# --- Jobs ---

# Task A — runs on any execute node
result_a = File("result-a.txt")
task_a = Job(task_a)
task_a.add_args("-o", result_a)
task_a.add_outputs(result_a)

wf.add_jobs(task_a)

wf.write("workflow.yml").plan(sites=["condorpool"], relative_dir="submit", submit=True)
