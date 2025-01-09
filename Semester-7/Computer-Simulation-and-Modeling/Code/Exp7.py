import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv('tsla_2014_2023.csv')

# 2. Plot the volume column
plt.hist(df['volume'], bins=100, density=True, alpha=0.7, color='g')
plt.title("Histogram of Tesla Stock volumes")
plt.xlabel("volume")
plt.ylabel("Density")
plt.show()

# 3. Fit Probability Distributions: Fit Normal and Exponential distributions to the volume data
fit_expon = stats.expon.fit(df['volume'])
fit_lognorm = stats.lognorm.fit(df['volume'])

# Plot the fitted distributions
x = np.linspace(min(df['volume']), max(df['volume']), 100)
pdf_expon = stats.expon.pdf(x, *fit_expon)
pdf_lognorm = stats.lognorm.pdf(x, *fit_lognorm)

plt.hist(df['volume'], bins=100, density=True, alpha=0.6, color='gray')
plt.plot(x, pdf_expon, 'r-', label="Exponential Fit")
plt.plot(x, pdf_lognorm, 'b-', label="Log Normal Fit")
plt.title("Fitting Distributions to volumes")
plt.xlabel("volume")
plt.ylabel("Density")
plt.legend()
plt.show()

# 4. Extract Parameters for the Fitted Distributions
print(f"Exponential Fit Parameters (loc, scale): {fit_expon}")
print(f"Log-Normal Fit Parameters (shape, loc, scale): {fit_lognorm}")

# 5. Goodness-of-Fit Testing using Kolmogorov-Smirnov (KS) test
ks_expon = stats.kstest(df['volume'], 'expon', args=fit_expon)
print(f"Kolmogorov-Smirnov test for Exponential: {ks_expon}")

ks_lognorm = stats.kstest(df['volume'], 'lognorm', args=fit_lognorm)
print(f"Kolmogorov-Smirnov test for Log Normal: {ks_lognorm}")

# 6. Chi-square goodness-of-fit test

# Observed frequencies (histogram data)
observed_freq, bins = np.histogram(df['volume'], bins=100)

# Expected frequencies (Exponential and Log-Normal)
expected_freq_expon = stats.expon.cdf(bins[1:], *fit_expon) - stats.expon.cdf(bins[:-1], *fit_expon)
expected_freq_lognorm = stats.lognorm.cdf(bins[1:], *fit_lognorm) - stats.lognorm.cdf(bins[:-1], *fit_lognorm)

# Normalize expected frequencies to match the observed sum
expected_freq_expon *= len(df['volume'])
expected_freq_lognorm *= len(df['volume'])

# Scale expected frequencies to match the total observed sum
expected_freq_expon *= observed_freq.sum() / expected_freq_expon.sum()
expected_freq_lognorm *= observed_freq.sum() / expected_freq_lognorm.sum()

# Perform the chi-square test
chi_square_expon = stats.chisquare(f_obs=observed_freq, f_exp=expected_freq_expon)
print(f"Chi-square test for Exponential: {chi_square_expon}")

chi_square_lognorm = stats.chisquare(f_obs=observed_freq, f_exp=expected_freq_lognorm)
print(f"Chi-square test for Log-Normal: {chi_square_lognorm}")
