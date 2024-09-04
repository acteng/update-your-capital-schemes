from locust import HttpUser, task, run_single_user, between


class SchemesUser(HttpUser):
    host = "http://127.0.0.1:5000"
    wait_time = between(1, 2)

    @task
    def show_schemes(self) -> None:
        self.client.get("/schemes")

    @task
    def show_scheme(self) -> None:
        self.client.get("/schemes/123")

    @task
    def change_spend_to_date(self) -> None:
        self.client.get("/schemes/123/spend-to-date")
        # TODO: post update

    @task
    def change_milestone_dates(self) -> None:
        self.client.get("/schemes/123/milestones")
        # TODO: post update

    @task
    def review_scheme(self) -> None:
        self.client.get("/schemes/123")
        # TODO: post update

    def on_start(self) -> None:
        # Trigger authentication
        self.client.get("/schemes")


if __name__ == "__main__":
    run_single_user(SchemesUser)
