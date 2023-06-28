import pandas as pd
from src.opynfield.config.defaults_settings import Defaults
from src.opynfield.config.user_input import UserInput
import os
from copy import deepcopy
from statsmodels.multivariate.manova import MANOVA
from statsmodels.formula.api import ols
from dataclasses import dataclass
from statsmodels.regression.linear_model import RegressionResultsWrapper
from statsmodels.stats.anova import anova_lm
import sys


def format_params(bounded_fits: dict[str, dict[str, dict[str, pd.DataFrame]]], defaults: Defaults,
                  user_inputs: UserInput) -> pd.DataFrame:
    dict_groups = {}
    for group in bounded_fits:
        group_df_list = []
        for x_measure in bounded_fits[group]:
            for y_measure in bounded_fits[group][x_measure]:
                df = bounded_fits[group][x_measure][y_measure]
                df = df.rename(columns=lambda x: f'{x_measure}_{y_measure}_parameter_{x}')
                group_df_list.append(df)
        full_group = pd.concat(group_df_list, axis=1)
        dict_groups[group] = full_group
        if defaults.save_group_model_csvs:
            # make a dir for results -> individuals -> group -> models
            path = user_inputs.result_path + '/Individuals/' + user_inputs.groups_to_paths[group] + '/Models'
            os.makedirs(path, exist_ok=True)
            df_path = path + '/IndividualModels.csv'
            full_group.to_csv(path_or_buf=df_path, index=False)
    for group, df in dict_groups.items():
        df['group'] = group
    f_df = pd.concat(dict_groups.values(), ignore_index=True)
    if defaults.save_all_group_model_csvs:
        path = user_inputs.result_path + '/Individuals/CombinedGroups/Models'
        os.makedirs(path, exist_ok=True)
        df_path = path + '/CombinedGroups_IndividualModels.csv'
        f_df.to_csv(path_or_buf=df_path, index=False)
    return f_df


def format_group_params(group_fits: dict[str, dict[str, dict[str, pd.DataFrame]]], defaults: Defaults,
                        user_inputs: UserInput):
    dict_groups = {}
    for group in group_fits:
        group_df_list = []
        for x_measure in group_fits[group]:
            for y_measure in group_fits[group][x_measure]:
                df = group_fits[group][x_measure][y_measure].T
                df = df.rename(columns=lambda x: f'{x_measure}_{y_measure}_parameter_{x}')
                group_df_list.append(df)
        full_group = pd.concat(group_df_list, axis=1)
        dict_groups[group] = full_group
        if defaults.save_group_model_csvs:
            # make a dir for results -> groups -> group -> models
            path = user_inputs.result_path + '/Groups/' + user_inputs.groups_to_paths[group] + '/Models'
            os.makedirs(path, exist_ok=True)
            df_path = path + '/GroupModels.csv'
            full_group.to_csv(path_or_buf=df_path, index=False)
    for group, df in dict_groups.items():
        df['group'] = group
    f_df = pd.concat(dict_groups.values(), ignore_index=True)
    if defaults.save_all_group_model_csvs:
        path = user_inputs.result_path + '/Groups/CombinedGroups/Models'
        os.makedirs(path, exist_ok=True)
        df_path = path + '/CombinedGroups_GroupModels.csv'
        f_df.to_csv(path_or_buf=df_path, index=False)
    return


def create_full_formula(test_df):
    vals_to_test = list(test_df.columns)
    vals_to_test.remove('group')
    formula = ''
    for v in range(len(vals_to_test)):
        if v < len(vals_to_test)-1:
            formula = formula + vals_to_test[v] + ' + '
        else:
            formula = formula + vals_to_test[v]
    formula = formula + ' ~ group'
    return formula


def run_full_test(formatted_bounded_fits: pd.DataFrame):
    test_df = deepcopy(formatted_bounded_fits).copy()
    full_formula = create_full_formula(test_df)
    model_full = MANOVA.from_formula(full_formula, data=test_df)
    print('Full Model MANOVA Results')
    print('\n')
    print(model_full.mv_test())
    return test_df


def get_col_names_from_prefix(test_df: pd.DataFrame, prefix: str) -> list[str]:
    cols_that_match = list()
    for c in test_df:
        if c.startswith(prefix):
            cols_that_match.append(c)
    return cols_that_match


def make_formula_from_list(dependent_vars: list[str], independent_var: str) -> str:
    formula = ' + '.join(dependent_vars) + f' ~ {independent_var}'
    return formula


@dataclass
class ManovaModels:
    full_model: MANOVA
    component_model_results: dict[str, RegressionResultsWrapper]
    independent_var: str

    def parameter_names(self):
        return list(self.component_model_results.keys())

    def display_results(self):
        p_names = self.parameter_names()
        name = '_'.join(p_names[0].split('_')[:-1])+'s'

        # display the full model results
        print(f'{name} MANOVA Results')
        print('\n')
        print(self.full_model.mv_test())

        # display the parameter model ANOVA results
        # and the pairwise t test
        for p in self.component_model_results:
            print(f'{p} ANOVA Results')
            print('\n')
            print((anova_lm(self.component_model_results[p])))
            print('\n')
            print(f'{p} Pairwise T-test Results')
            print('\n')
            frame = self.component_model_results[p].t_test_pairwise(self.independent_var).result_frame
            print(frame)
            print('\n')
        return


def generate_models(test_df: pd.DataFrame, prefix: str, independent_var: str = 'group'):
    cols_that_match = get_col_names_from_prefix(test_df, prefix)
    full_formula = make_formula_from_list(dependent_vars=cols_that_match, independent_var=independent_var)
    # full model
    model_f = MANOVA.from_formula(full_formula, data=test_df)
    # model for each var
    component_model_results = dict()
    for c in cols_that_match:
        formula_c = make_formula_from_list(dependent_vars=[c], independent_var=independent_var)
        model_result_c = ols(formula_c, test_df).fit()
        component_model_results[c] = model_result_c
    models = ManovaModels(full_model=model_f, component_model_results=component_model_results,
                          independent_var=independent_var)
    return models


def run_component_tests(test_df: pd.DataFrame, defaults: Defaults):
    for test_param in defaults.create_pairs():
        models = generate_models(test_df, test_param)
        models.display_results()
    return


def run_tests(formatted_bounded_fits: pd.DataFrame, defaults: Defaults,
              user_inputs: UserInput):
    os.makedirs(user_inputs.result_path+'/Stats')
    stats_results_file = user_inputs.result_path + '/Stats/results.txt'
    orig_stdout = sys.stdout
    f = open(stats_results_file, 'a')
    sys.stdout = f
    test_df = run_full_test(formatted_bounded_fits)
    run_component_tests(test_df, defaults)
    sys.stdout = orig_stdout
    f.close()
    return
