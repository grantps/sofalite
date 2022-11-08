ci_explain = ('There is a 95% chance the population mean is within the '  ## is using % in string interpolation in ultimate destination so 95%% not 95%
    "confidence interval calculated for this sample. Don't forget, of course, "
    'that the population mean could lie well outside the interval bounds. Note'
    ' - many statisticians argue about the best wording for this conclusion.')

kurtosis_explain = ('Kurtosis measures the peakedness or flatness of values. '
    ' Between -2 and 2 means kurtosis is unlikely to be a problem. Between -1 '
    'and 1 means kurtosis is quite unlikely to be a problem.')

normality_measure_explain = ('This provides a single measure of normality. If p'
    ' is small, e.g. less than 0.01, or 0.001, you can assume the distribution'
    ' is not strictly normal. Note - it may be normal enough though.')

obrien_explain = ('If the value is small, e.g. less than 0.01, or 0.001, you '
    'can assume there is a difference in variance.')

one_tail_explain = (
    'This is a one-tailed result i.e. based on the likelihood of a difference '
    "in one particular direction")

p_explain_multiple_groups = (
    'If p is small, e.g. less than 0.01, or 0.001, you can assume the result '
    'is statistically significant i.e. there is a difference between at least '
    'two groups. Note: a statistically significant difference may not '
    'necessarily be of any practical significance.')

skew_explain = ('Skew measures the lopsidedness of values. '
    ' Between -2 and 2 means skew is unlikely to be a problem. Between -1 '
    'and 1 means skew is quite unlikely to be a problem.')

std_dev_explain = 'Standard Deviation measures the spread of values.'
