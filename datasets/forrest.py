from benchopt import BaseDataset, safe_import_context


# Protect the import with `safe_import_context()`. This allows:
# - skipping import to speed up autocompletion in CLI.
# - getting requirements info when all dependencies are not installed.
with safe_import_context() as import_ctx:
    from nilearn import masking, maskers
    from benchmark_utils.config import DATA_PATH_FORREST, MEMORY
    from pathlib import Path
    import pandas as pd
    from nilearn import image


# All datasets must be named `Dataset` and inherit from `BaseDataset`
class Dataset(BaseDataset):
    # Name to select the dataset in the CLI and to display the results.
    name = "Forrest"

    # List of parameters to generate the datasets. The benchmark will consider
    # the cross product for each key in the dictionary.
    # Any parameters 'param' defined here is available as `self.param`.
    parameters = {
        "target": [
            "sub-01",
            "sub-02",
            "sub-03",
            "sub-04",
            "sub-05",
            "sub-06",
            "sub-07",
            "sub-08",
            "sub-10",
            "sub-11",
        ],
    }

    # List of packages needed to run the dataset. See the corresponding
    # section in objective.py
    requirements = []

    def __init__(self, target):
        self.subjects = [
            "sub-01",
            "sub-02",
            "sub-03",
            "sub-04",
            "sub-05",
            "sub-06",
            "sub-07",
            "sub-08",
            "sub-10",
            "sub-11",
        ]
        self.target = target

    def load_ibc_sound(self, subject, data_path):
        alignment_contrasts = image.load_img(
            data_path / "derivatives" / f"gm_3mm_{subject}.nii.gz"
        )
        decoding_contrasts = image.load_img(
            data_path / "derivatives" / f"forrest_gm_3mm_{subject}.nii.gz"
        )
        labels = pd.read_csv(
            data_path / "derivatives" / f"{subject}_labels.csv",
            header=None,
        ).values.ravel()
        return alignment_contrasts, decoding_contrasts, labels

    def get_data(self):
        # The return arguments of this function are passed as keyword arguments
        # to `Objective.set_data`. This defines the benchmark's
        # API to pass data. It is customizable for each benchmark.
        data_path = Path(DATA_PATH_FORREST)

        # Create a masker to extract the data from the brain volume.
        masker_path = data_path / "gm_mask_3mm.nii.gz"
        connected_mask = masking.compute_background_mask(
            masker_path, connected=True
        )
        mask = maskers.NiftiMasker(connected_mask, memory=MEMORY).fit()

        dict_alignment = dict()
        dict_decoding = dict()
        dict_labels = dict()
        for subject in self.subjects:
            (
                alignment_contrasts,
                decoding_contrasts,
                labels,
            ) = self.load_ibc_sound(subject, data_path)
            dict_labels[subject] = labels

            if subject == self.target:
                data_alignment_target = alignment_contrasts
                data_decoding_target = decoding_contrasts
            else:
                dict_alignment[subject] = alignment_contrasts
                dict_decoding[subject] = decoding_contrasts

        # The dictionary defines the keyword arguments for `Objective.set_data`
        return dict(
            dict_alignment=dict_alignment,
            dict_decoding=dict_decoding,
            data_alignment_target=data_alignment_target,
            data_decoding_target=data_decoding_target,
            dict_labels=dict_labels,
            target=self.target,
            mask=mask,
        )
