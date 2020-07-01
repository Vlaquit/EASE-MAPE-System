from analysis.problem import AdaptationProblem, solve_optimization_problem
from analysis.analysis import Analysis
from monitoring.docker_monitoring import DockerMonitoring


class OptimizationAnalysis(Analysis):
    H = 10
    response_time_upper_bound = 100
    response_time_lower_bound = 0.01
    container_capacity_lower_bound = 10
    container_capacity_upper_bound = 1000
    revenue_per_thousand_ads = 100
    banner_count_lower_bound = 1
    banner_count_upper_bound = 10
    data_transfer_cost = 0.0001
    container_cost = 0.0002

    def __init__(self, mongo_client):
        # setting constants
        super().__init__(mongo_client)
        self.nb_containers = 0

    def update(self):
        last_data = super().get_last_data()
        self.nb_containers = last_data.get("nb_containers")
        total_net_usage = last_data.get('net_rx') + last_data.get('net_tx')
        problem = AdaptationProblem(
            landa=self.get_request_count() / self.get_monitoring_time(),
            n=total_net_usage / self.get_request_count(),
            p_i=self.container_cost,
            p_n=self.data_transfer_cost,
            H=self.H,
            RPM=self.revenue_per_thousand_ads,
            R=self.get_response_time(),
            gamma_l=self.banner_count_lower_bound,
            gamma_u=self.banner_count_upper_bound,
            R_l=self.response_time_lower_bound,
            R_u=self.response_time_lower_bound,
            d_l=self.container_capacity_lower_bound,
            d_u=self.container_capacity_upper_bound
        )
        objectives, variables = solve_optimization_problem(problem)
        print("Analyse results:")
        print(f"p_s should be {variables[0]}")
        print(f"W should be {variables[1]}")
        print(f"gamma should be {variables[2]}")
        print("in optimal conditions:")
        print(f"service profit should be {objectives[0]}")
        print(f"client profit should be {objectives[1]}")
        print(f"user satisfaction should be {objectives[2]}")
        # we can also insert results into some sort of database
        super().notify()

    def get_response_time(self):
        # TODO:save it in workload generator
        return 0.6

    def get_request_count(self):
        # TODO:save it in workload generator or app
        return 1000

    def get_monitoring_time(self):
        return DockerMonitoring.interval  # in seconds
