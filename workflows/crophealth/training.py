# Image preprocessing parameters
IMAGE_SIZE = 128  # Target image size (square)
TRAIN_SPLIT = 0.8  # Fraction of data for training

# Model training parameters
EPOCHS = 10  # Number of training epochs
BATCH_SIZE = 16  # Training batch size

import os
import logging
import argparse
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
    wf_name = "crophealth-training"

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

        preprocess_images = Transformation(
            "preprocess_images",
            site=exec_site_name,
            pfn=os.path.join(self.wf_dir, "bin/preprocess_images.py"),
            is_stageable=True,
            container=crophealth_container,
        ).add_pegasus_profile(queue=os.environ["SLURM_GPU_PARTITION"])

        train_classifier = Transformation(
            "train_classifier",
            site=exec_site_name,
            pfn=os.path.join(self.wf_dir, "bin/train_classifier.py"),
            is_stageable=True,
            container=crophealth_container,
        ).add_pegasus_profile(queue=os.environ["SLURM_GPU_PARTITION"])

        if os.environ.get("RESOURCE") == "ANVIL":
            preprocess_images.add_pegasus_profile(
                glite_arguments=f"--gres:gpu:1 --mem={self.MEM}"
            )
            train_classifier.add_pegasus_profile(
                glite_arguments=f"--gres:gpu:1 --mem={self.MEM}"
            )
        else:
            preprocess_images.add_pegasus_profile(
                gpus="1", glite_arguments=f"--mem={self.MEM}"
            )
            train_classifier.add_pegasus_profile(
                gpus="1", glite_arguments=f"--mem={self.MEM}"
            )

        self.tc.add_containers(crophealth_container)
        self.tc.add_transformations(
            preprocess_images,
            train_classifier,
        )

    def create_workflow(self, args):
        """Create the complete workflow."""
        self.wf = Workflow(self.wf_name)

        # inputs
        catalog_file = File("crop_catalog.csv")
        images_archive = File("images.tar.gz")

        # simplified inputs - these were originally downloaded from Kaggle
        self.rc.add_replica(
            "remote",
            catalog_file,
            f"https://download.pegasus.isi.edu/tutorial/crophealth/{catalog_file}",
        )
        self.rc.add_replica(
            "remote",
            images_archive,
            f"https://download.pegasus.isi.edu/tutorial/crophealth/{images_archive}",
        )

        # Output file names
        train_data = File("train_data.npz")
        val_data = File("val_data.npz")
        label_mapping = File("label_mapping.json")
        preprocessing_info = File("preprocessing_info.json")
        model_checkpoint = File("disease_classifier.pt")
        training_info = File("training_info.json")
        predictions_file = File("predictions.json")

        # Job 1: Preprocess images
        preprocess_job = Job(
            "preprocess_images", _id="preprocess", node_label="preprocess"
        )
        preprocess_job.add_args(
            "--input",
            catalog_file,
            "--output-dir",
            ".",
            "--image-size",
            str(args.image_size),
            "--split",
            str(args.train_split),
            "--images-archive",
            images_archive,
        )
        preprocess_job.add_inputs(catalog_file, images_archive)
        preprocess_job.add_outputs(train_data, stage_out=True, register_replica=False)
        preprocess_job.add_outputs(val_data, stage_out=True, register_replica=False)
        preprocess_job.add_outputs(
            label_mapping, stage_out=True, register_replica=False
        )
        preprocess_job.add_outputs(
            preprocessing_info, stage_out=True, register_replica=False
        )
        preprocess_job.add_pegasus_profile(label="preprocess")

        # Job 2: Train classifier
        train_job = Job("train_classifier", _id="train", node_label="train")
        train_job.add_args(
            "--input-dir",
            ".",
            "--output-dir",
            ".",
            "--epochs",
            str(args.epochs),
            "--batch-size",
            str(args.batch_size),
        )
        train_job.add_inputs(train_data, val_data, label_mapping)
        train_job.add_outputs(model_checkpoint, stage_out=True, register_replica=False)
        train_job.add_outputs(training_info, stage_out=True, register_replica=False)
        train_job.add_pegasus_profile(label="train")

        # Add jobs to workflow
        self.wf.add_jobs(preprocess_job, train_job)

        # Define dependencies
        self.wf.add_dependency(preprocess_job, children=[train_job])


# --- Build and generate the workflow ---
dagfile = "workflow.yml"

args = argparse.Namespace(
    image_size=IMAGE_SIZE,
    train_split=TRAIN_SPLIT,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
)

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
workflow.create_workflow(args)

workflow.write()
print("\nCrop Health Workflow has been generated!")

workflow.plan_submit()
