from numpy import sqrt
import random as r, os

os.system('cls' if os.name == 'nt' else 'clear')

population = [r.randint(0, 100) for i in range(10000000)]
pop_mean = sum(population) / len(population)
pop_variance = sum((x - pop_mean) ** 2 for x in population) / len(population)
pop_stdev = sqrt(pop_variance)

sample = [r.choice(population) for i in range(1000)]
sample_mean = sum(sample) / len(sample)
sample_unbiased_variance = sum((x - sample_mean) ** 2 for x in sample) / (len(sample) - 1)
sample_stdev = sqrt(sample_unbiased_variance)
sample_biased_variance = sum((x - sample_mean) ** 2 for x in sample) / len(sample)

sample_biased_stdev = sqrt(sample_biased_variance)

print(pop_variance, sample_unbiased_variance, sample_biased_variance)
print(pop_stdev, sample_stdev, sample_biased_stdev)