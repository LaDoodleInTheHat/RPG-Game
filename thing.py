g_one = int(input(" >>> "))
g_two = int(input(" >>> "))


equation = lambda x: x**2+10

thing = (equation(g_one) - equation(g_two)) / (g_one - g_two)

print(thing)