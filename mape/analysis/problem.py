import numpy as np
from pymoo.algorithms.nsga2 import NSGA2
from pymoo.factory import get_problem, get_termination
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
from pymoo.model.problem import Problem


class AdaptationProblem(Problem):

    def __init__(self,
                 landa=1000,
                 n=10,
                 p_i=0.0002,
                 p_n=0.0001,
                 H=0.0002,
                 RPM=100,
                 R=0.6,
                 gamma_l=1,
                 gamma_u=10,
                 R_l=0.01,
                 R_u=10.0,
                 d_l=10,
                 d_u=1000
                 ):
        """

        :param landa: request arrival rate (req/s)
        :param n: average data payload for each request (KB)
        :param p_i: cost of a VM ($/s)
        :param p_n: cost of data transfer ($/KB)
        :param H: static Hosting cost ($/s)
        :param RPM: revenue per 1000 ads ($)
        :param R: response time (s)
        :param gamma_l: gamma lower bound (gamma is average number of ad banners per page)
        :param gamma_u: gamma upper bound
        :param R_l: response time lower bound
        :param R_u: response time upper bound
        :param d_l: capacity of each VM lower bound(request/s)
        :param d_u: capacity of each VM upper bound(request/s)
        """
        self.landa = landa
        self.n = n
        self.p_i = p_i
        self.p_n = p_n
        self.H = H
        self.RPM = RPM
        self.R = R
        self.gamma_l = gamma_l
        self.gamma_u = gamma_u
        self.R_l = R_l
        self.R_u = R_u
        self.d_l = d_l
        self.d_u = d_u
        # weights in user satisfaction formula
        self.a = 0.5
        self.b = 0.5
        # p_s doesn't have any bound so we should feed algorithm
        # a very high number for upper bound and 0 (logically) for lower bound
        super().__init__(n_var=3,  # p_s,W,gamma
                         n_obj=3,  # pi_s,pi_a,U
                         n_constr=4,
                         xl=np.array([100000, landa / d_u, gamma_l]),
                         xu=np.array([0, landa / d_l, gamma_u]))

    def _evaluate(self, x, out, *args, **kwargs):
        # objectives
        # to maximize objectives we multipy them by -1 and then minimize them
        # objectives are not normalized. test normalization on results
        pi_s = x[:, 0] * self.landa - self.p_i * x[:, 1] - self.n * self.p_n * self.landa
        pi_a = (x[:, 2] * self.RPM / 1000) * self.landa - self.H * self.landa - x[:, 0] * self.landa
        U = self.a * ((self.gamma_u - x[:, 2]) / (self.gamma_u - self.gamma_l)) + self.b * (
                (self.R_u - self.R) / (self.R_u - self.R_l))

        out["F"] = np.column_stack([-1 * pi_s, -1 * pi_a, -1 * U])

        # constrains (equations are filped in a way that they would be less than zero)
        g1 = x[:, 0] - (x[:, 2] * self.RPM) / 1000
        g2 = -1 * pi_s
        g3 = -1 * pi_a
        g4 = 0.8 - U

        out["G"] = np.column_stack([g1, g2, g3, g4])


def solve_optimization_problem(problem: AdaptationProblem):
    # defining algorithm
    algorithm = NSGA2(
        pop_size=100,
        n_offsprings=10,
        eliminate_duplicates=True
    )

    # defining termination
    termination = get_termination('n_gen', 500)

    # solving problem and getting the results
    res = minimize(problem,
                   algorithm,
                   termination,
                   seed=1,
                   save_history=True,
                   verbose=True
                   )

    # you can find objectives in res.F and variables in res.X
    return res.F, res.X
