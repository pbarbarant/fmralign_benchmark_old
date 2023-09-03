from benchopt import BaseObjective, safe_import_context

# Protect the import with `safe_import_context()`. This allows:
# - skipping import to speed up autocompletion in CLI.
# - getting requirements info when all dependencies are not installed.
with safe_import_context() as import_ctx:
    import numpy as np
    from sklearn.svm import LinearSVC
    from sklearn.preprocessing import StandardScaler

# The benchmark objective must be named `Objective` and
# inherit from `BaseObjective` for `benchopt` to work properly.
class Objective(BaseObjective):

    # Name to select the objective in the CLI and to display the results.
    name = "fMRI decoding"

    # URL of the main repo for this benchmark.
    url = "https://github.com/pbarbarant/fmralign_benchmark_old"

    # List of parameters for the objective. The benchmark will consider
    # the cross product for each key in the dictionary.
    # All parameters 'p' defined here are available as 'self.p'.
    # This means the OLS objective will have a parameter `self.whiten_y`.
    parameters = {}

    # List of packages needed to run the benchmark.
    # They are installed with conda; to use pip, use 'pip:packagename'. To
    # install from a specific conda channel, use 'channelname:packagename'.
    # Packages that are not necessary to the whole benchmark but only to some
    # solvers or datasets should be declared in Dataset or Solver (see
    # simulated.py and python-gd.py).
    # Example syntax: requirements = ['numpy', 'pip:jax', 'pytorch:pytorch']
    requirements = ['fmralign', 'scikit-learn', 'numpy']

    # Minimal version of benchopt required to run this benchmark.
    # Bump it up if the benchmark depends on a new feature of benchopt.
    min_benchopt_version = "1.4"

    def set_data(self, dict_alignment, dict_decoding, data_alignment_target, data_decoding_target, dict_labels, target, mask):
        # The keyword arguments of this function are the keys of the dictionary
        # returned by `Dataset.get_data`. This defines the benchmark's
        # API to pass data. This is customizable for each benchmark.
        self.dict_alignment = dict_alignment
        self.dict_decoding = dict_decoding
        self.data_alignment_target = data_alignment_target
        self.data_decoding_target = data_decoding_target
        self.dict_labels = dict_labels
        self.target = target
        self.mask = mask

    def compute(self, dict_alignment_estimators):
        # The keyword arguments of this function are the keys of the
        # dictionary returned by `Solver.get_result`. This defines the
        # benchmark's API to pass solvers' result. This is customizable for
        # each benchmark.
        X_train = []
        y_train = []
        
        # print("dict_alignment_estimators", dict_alignment_estimators['sub-03'])
        for subject in self.dict_alignment.keys():
            alignment_estimator = dict_alignment_estimators[subject]
            data_decoding = self.dict_decoding[subject]
            aligned_data = alignment_estimator.transform(data_decoding)
            X_train.append(self.mask.transform(aligned_data))
            labels = self.dict_labels[subject]
            y_train.append(labels)
            
        se = StandardScaler()
        X_train = np.vstack(X_train)
        X_train = se.fit_transform(X_train)
        y_train = np.hstack(y_train).reshape(-1, 1)
        
        print("Fitting LinearSVC")
        clf = LinearSVC(max_iter=100)
        clf.fit(X_train, y_train)        
        
        X_test = self.mask.transform(self.data_decoding_target)
        X_test = se.transform(X_test)
        y_test = self.dict_labels[self.target].reshape(-1, 1)
        
        score = clf.score(X_test, y_test)
        # This method can return many metrics in a dictionary. One of these
        # metrics needs to be `value` for convergence detection purposes.
        return dict(
            value=score,
        )

    def get_one_result(self):
        # Return one solution. The return value should be an object compatible
        # with `self.evaluate_result`. This is mainly for testing purposes.
        return dict(dict_alignment_estimators={})

    def get_objective(self):
        # Define the information to pass to each solver to run the benchmark.
        # The output of this function are the keyword arguments
        # for `Solver.set_objective`. This defines the
        # benchmark's API for passing the objective to the solver.
        # It is customizable for each benchmark.
        return dict(
            dict_alignment=self.dict_alignment,
            data_alignment_target=self.data_alignment_target,
            mask=self.mask,
        )
