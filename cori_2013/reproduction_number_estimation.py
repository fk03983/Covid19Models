import numpy as np
from scipy import stats
import matplotlib.pyplot as plt





def prior_instant_R_t(t):
    if t <= 15:
        return 2.5
    return 0.7

def estimate_I_t(t, instant_R_t, incidence_data, w):
    '''
    :param t: t (in days) at which to estimate I_t
    :param instant_R_t: a function of the form f(t) which returns the reproduction number at a given time t.
    :param incidence_data: a list of integers. indcidence_data[s] represents the number of incident cases on day s.
    :param w: a probability density function describing the infectious profile with signature f(t) where is an integer. w(s) represents the probability of spreading the infection on day s.
    :return: prediction of the number of incidence cases on day t.

    Follwing appendix 1 of cori 2013. I_t follows a poisson distribution. (See eq. 1 of equations page)
    '''

    #summation = 0
    #for s in range(t):
    #    summation += (incidence_data[s] * w(s))

    summation = lambda_t(t, incidence_data, w)


    mean = prior_instant_R_t(t) * summation #mean of poisson distribution

    estimate = np.random.poisson(mean) #sample
    return estimate

def lambda_t(t, incidence_data, w):
    """
    :param indidence_data: a list of integers. indcidence_data[s] represents the number of incident cases on day s.
    :param w: a probability density function describing the infectious profile with signature f(t) where is an integer. w(s) represents the probability of spreading the infection on day s.
    :return: a float representing the summation

    Following appendex 1 of cori 2013. See (eq.3 of equations)
    """
    summation = 0
    for s in range(1, t+1 ):
        summation += (incidence_data[t-s] * w(s))

    return summation




def estimate_R_t(t, pi, incidence_data, w, a = 1, b = 5):
    """
    :param t: t (in days) at which to re_estimate R_t
    :param pi: the size of the window
    :param incidence_data: a list of integers. indcidence_data[s] represents the number of incident cases on day s.
    :param w: a probability density function describing the infectious profile with signature f(t) where is an integer. w(s) represents the probability of spreading the infection on day s.
    :param a, b: constants to be used in gamma distribution of a.
    :return: an estimate of Reproduction number on day t.
    Follwing appendix 1 of cori 2013. I_t follows a poisson distribution. (See eq. 2 of equations page)
    """

    summation = 0
    summation_lambdas = 0
    for s in range(t - pi, t):
        summation += (incidence_data[s])
        summation_lambdas = lambda_t(s)

    alpha = a + summation
    beta = (1/b) + summation_lambdas

    estimate = np.random.gamma(alpha, 1/beta)
    return estimate

def infection_profile(mean, std_deviation):
    """
    :param mean: mean of the gamma distribution that the infection profile follows.
    :param std_deviation: std_deviation of the gamma distribution that the infection profile follows.
    :param s: day at which to determine probability.
    :return: descritized probability of the infection profile at day s.

    Following shifted gamma distribution on appendix 11
    """

    beta = mean / (std_deviation ** 2) #since, mean = alpha/beta and variance = alpha/(beta^2)
    alpha = mean * beta


    def prob(s):

        int_s = int(s)
        assert np.allclose([int_s], [s])  # making sure s is an integer
        s += 1
        prob = (np.convolve(s,stats.gamma.cdf(s, a = alpha, scale = 1/beta))) + (np.convolve((s - 2), stats.gamma.cdf(s - 2, a = alpha, scale = 1/beta)) ) - \
               (np.convolve(2,  np.convolve((s - 1) , stats.gamma.cdf(s - 1, a = alpha, scale = 1/beta)))) + \
               ((alpha * 1/beta)*(2*(stats.gamma.cdf(s-1, a = alpha + 1, scale = 1/beta))- stats.gamma.cdf(s - 2, a = alpha + 1, scale = 1/beta) - \
                                  stats.gamma.cdf(s, a = alpha + 1, scale = 1/beta)))


        return prob[0]
    return prob

if __name__ == "__main__":
    """Following appendix 6"""
    T = 50

    incidence_across_simulations = [[] for i in range(1, T+1)]
    for i in range(100):
        mean = 8.4
        std_deviation = 3.8
        incidence_data = [0,10]
        w = infection_profile(mean, std_deviation)
        probs = []

        for t in range(10):
            probs.append(w(t))

        for t in range(2, T+1):
            incidence_data.append(estimate_I_t(t, instant_R_t= prior_instant_R_t, w = w, incidence_data=incidence_data))

        for i in range(len(incidence_data[1:])):
            incidence_across_simulations[i].append(incidence_data[i+1])


        """ 
        plt.scatter(range(10), probs)
        plt.xlabel("Serial Interval (Days)")
        plt.ylabel("Probability")
        plt.show()
        """
        print(len(range(T)), len(incidence_data))
        plt.scatter(range(T), incidence_data[1:], color = "black", marker='x')

        print(min(incidence_data), max(incidence_data), np.mean(incidence_data))

    means = [np.mean(i) for i in incidence_across_simulations]
    plt.plot(range(T), means,  color = "red")

    plt.xlabel("Time (Days)")
    plt.ylabel("Incidence")
    plt.show()












