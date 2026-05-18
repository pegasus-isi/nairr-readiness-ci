import os
import logging
from pathlib import Path

from Pegasus.api import *

logging.basicConfig(level=logging.DEBUG)


class CropHealthWorkflow:
    """Generate Pegasus workflow for crop disease detection."""

    MEM = "21G"

    wf = None
    sc = None
    tc = None
    rc = None
    props = None

    dagfile = None
    wf_dir = None
    shared_scratch_dir = None
    local_storage_dir = None
    wf_name = "crophealth-inference"

    def __init__(self, dagfile="workflow.yml"):
        """Initialize workflow."""
        self.dagfile = dagfile
        self.wf_dir = str(Path(".").resolve())
        self.shared_scratch_dir = os.path.join(self.wf_dir, "scratch")
        self.local_storage_dir = os.path.join(self.wf_dir, "output")

    def write(self):
        """Write all catalogs and workflow to files."""
        if self.sc is not None:
            self.sc.write()
        self.props.write()
        self.rc.write()
        self.tc.write()
        try:
            self.wf.write(file=self.dagfile)
        except PegasusClientError as e:
            print(e)

    def plan_submit(self):
        """Plan and submit the workflow."""
        try:
            self.wf.plan(submit=True, relative_dir="submit")
        except PegasusClientError as e:
            print(e)

    def status(self):
        """Get workflow status."""
        try:
            self.wf.status(long=True)
        except PegasusClientError as e:
            print(e)

    def wait(self):
        """Wait for workflow completion."""
        try:
            self.wf.wait()
        except PegasusClientError as e:
            print(e)

    def statistics(self):
        """Get workflow statistics."""
        try:
            self.wf.statistics()
        except PegasusClientError as e:
            print(e)

    def create_pegasus_properties(self):
        """Create Pegasus properties configuration."""
        self.props = Properties()
        self.props["pegasus.mode"] = "development"

    def create_sites_catalog(self, exec_site_name="condorpool"):
        """Create site catalog."""
        self.sc = SiteCatalog()

        local = Site("local").add_directories(
            Directory(Directory.LOCAL_STORAGE, self.local_storage_dir).add_file_servers(
                FileServer("file://" + self.local_storage_dir, Operation.ALL)
            ),
            Directory(
                Directory.SHARED_SCRATCH, self.shared_scratch_dir
            ).add_file_servers(
                FileServer("file://" + self.shared_scratch_dir, Operation.ALL)
            ),
        )

        if os.path.exists("pegasus_lite_env_source"):
            local.add_pegasus_profile(
                pegasus_lite_env_source=os.path.abspath("pegasus_lite_env_source")
            )

        local_scratch_var = os.environ["SITE_LOCAL_SCRATCH_VAR"]
        local_scratch = os.environ[local_scratch_var]
        exec_site = (
            Site(exec_site_name)
            .add_directories(
                Directory(
                    Directory.SHARED_SCRATCH,
                    self.shared_scratch_dir,
                    shared_file_system=True,
                ).add_file_servers(
                    FileServer("file://" + self.shared_scratch_dir, Operation.ALL)
                ),
                Directory(Directory.LOCAL_SCRATCH, local_scratch).add_file_servers(
                    FileServer("file://" + local_scratch, Operation.ALL)
                ),
            )
            .add_condor_profile(grid_resource="batch slurm")
            .add_pegasus_profile(
                style="glite",
                queue=os.environ["SLURM_CPU_PARTITION"],
                project=os.environ["SLURM_ACCOUNT"],
                data_configuration="nonsharedfs",
                auxillary_local="true",
                runtime=3600,
            )
        )

        if os.environ.get("RESOURCE") == "EXPANSE":
            exec_site.add_pegasus_profile(nodes=1, cores=1)

        self.sc.add_sites(local, exec_site)

    def create_replica_catalog(self):
        """Create replica catalog for input files."""
        self.rc = ReplicaCatalog()

    def create_transformation_catalog(self, exec_site_name="condorpool"):
        """Create transformation catalog with executables and containers."""
        self.tc = TransformationCatalog()

        crophealth_container = Container(
            "crophealth_container",
            container_type=Container.SINGULARITY,
            image="https://download.pegasus.isi.edu/tutorial/crophealth/crophealth-container.sif",
            image_site="www",
        )

        classify_disease = (
            Transformation(
                "classify_disease",
                site=exec_site_name,
                pfn=os.path.join(self.wf_dir, "bin/classify_disease.py"),
                is_stageable=True,
                container=crophealth_container,
            )
            .add_pegasus_profile(gpus="1")
            .add_pegasus_profile(glite_arguments="--mem=21G")
            .add_pegasus_profile(queue=os.environ["SLURM_GPU_PARTITION"])
        )
        if os.environ.get("RESOURCE") == "ANVIL":
            classify_disease.add_pegasus_profile(
                project=os.environ["SLURM_ACCOUNT"] + "-gpu",
                glite_arguments=f"--gres=gpu:1 --qos=gpu --mem={self.MEM}"
            )
        else:
            classify_disease.add_pegasus_profile(
                gpus="1", glite_arguments=f"--mem={self.MEM}"
            )

        self.tc.add_containers(crophealth_container)
        self.tc.add_transformations(classify_disease)

    def create_workflow(self):
        """Create the complete workflow."""
        self.wf = Workflow(self.wf_name)

        # common inputs
        model_checkpoint = File("disease_classifier.pt")
        training_info = File("training_info.json")

        # input locations - these would be generated by the previous training job, but we provide
        # standalone inputs here to that the inference workflow is independent from the training
        # workflow
        self.rc.add_replica(
            "remote",
            model_checkpoint,
            f"https://download.pegasus.isi.edu/tutorial/crophealth/{model_checkpoint}",
        )
        self.rc.add_replica(
            "remote",
            training_info,
            f"https://download.pegasus.isi.edu/tutorial/crophealth/{training_info}",
        )

        # sample input images from https://download.pegasus.isi.edu/tutorial/crophealth/inference/
        for image_num in range(10):
            image_id = f"{image_num:02d}"

            # inputs
            image_file = File(f"{image_id}.jpg")
            self.rc.add_replica(
                "remote",
                image_file,
                f"https://download.pegasus.isi.edu/tutorial/crophealth/inference/{image_file}",
            )

            # outputs
            predictions_file = File(f"{image_id}_predictions.json")

            # Job: Classify diseases
            classify_job = Job(
                "classify_disease",
                _id=f"classify_{image_id}",
                node_label=f"classify_{image_id}",
            )
            classify_job.add_args("--input", image_file, "--output", predictions_file)
            classify_job.add_inputs(model_checkpoint, training_info, image_file)
            classify_job.add_outputs(
                predictions_file, stage_out=True, register_replica=False
            )

            # add job
            self.wf.add_jobs(classify_job)


# --- Build and generate the workflow ---
dagfile = "workflow.yml"

workflow = CropHealthWorkflow(dagfile=dagfile)

print("Creating execution sites...")
workflow.create_sites_catalog("condorpool")

print("Creating workflow properties...")
workflow.create_pegasus_properties()

print("Creating transformation catalog...")
workflow.create_transformation_catalog("condorpool")

print("Creating replica catalog...")
workflow.create_replica_catalog()

print("Creating crop health workflow DAG...")
workflow.create_workflow()

workflow.write()
print("\nCrop Health Workflow has been generated!")

workflow.plan_submit()
