import pickle as pkl
import statsmodels.formula.api as smf


def run_func(f, fp, *args, **kwargs):
    try:
        with open(fp, 'rb') as file:
            result = pkl.load(file)
    except FileNotFoundError:
        result = f(*args, **kwargs)
        with open(fp, 'wb') as file:
            pkl.dump(result, file)
    return result


def run_ols(formula, data):
    result = smf.ols(formula=formula, data=data).fit()
    print(result.summary())
    return result

