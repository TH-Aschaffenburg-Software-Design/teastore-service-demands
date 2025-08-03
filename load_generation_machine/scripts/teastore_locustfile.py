import logging
from random import choice, randint

from locust import FastHttpUser, constant_throughput, task
from locust.contrib.fasthttp import FastResponse

path = "/tools.descartes.teastore.webui"


class UserBehavior(FastHttpUser):

    wait_time = constant_throughput(20)

    @task
    def user_flow(self) -> None:
        """
        Simulates user behaviour.
        :return: None
        """
        logging.info("Starting user.")
        self.visit_home()
        self.login()
        self.browse()
        # 50/50 chance to buy
        choice_buy = choice([True, False])
        if choice_buy:
            self.buy()
        self.visit_profile()
        self.logout()
        logging.info("Completed user.")

    def login(self) -> None:
        """
        User login with random userid between 1 and 90.
        :return: categories
        """
        logging.info("Starting user.")
        # load login page
        res = self.client.get(path + "/login")
        if isinstance(res, FastResponse) and res.ok:
            logging.info("Loaded login page.")
        else:
            logging.error(f"Could not load login page: {res.status_code}")
        # login random user
        user = randint(1, 99)
        login_request = self.client.post(
            path + "/loginAction", params={"username": user, "password": "password"}
        )
        if isinstance(login_request, FastResponse) and login_request.ok:
            logging.info(f"Login with username: {user}")
        else:
            logging.error(
                f"Could not login with username: {user} - status: {login_request.status_code}"
            )

    def visit_home(self) -> None:
        """
        Visits the landing page.
        :return: None
        """
        # load landing page
        res = self.client.get(path + "/")
        if isinstance(res, FastResponse) and res.ok:
            logging.info("Loaded landing page.")
        else:
            logging.error(f"Could not load landing page: {res.status_code}")

    def browse(self) -> None:
        """
        Simulates random browsing behaviour.
        :return: None
        """
        # execute browsing action randomly up to 5 times
        for i in range(1, randint(2, 5)):
            # browses random category and page
            category_id = randint(2, 6)
            page = randint(1, 5)
            category_request = self.client.get(
                path + "/category", params={"page": page, "category": category_id}
            )
            if isinstance(category_request, FastResponse) and category_request.ok:
                logging.info(f"Visited category {category_id} on page 1")
                # browses random product
                product_id = randint(7, 506)
                product_request = self.client.get(
                    path + "/product", params={"id": product_id}
                )
                if isinstance(product_request, FastResponse) and product_request.ok:
                    logging.info(f"Visited product with id {product_id}.")
                    cart_request = self.client.post(
                        path + "/cartAction",
                        params={"addToCart": "", "productid": product_id},
                    )
                    if isinstance(cart_request, FastResponse) and cart_request.ok:
                        logging.info(f"Added product {product_id} to cart.")
                    else:
                        logging.error(
                            f"Could not put product {product_id} in cart - status {cart_request.status_code}"
                        )
                else:
                    logging.error(
                        f"Could not visit product {product_id} - status {product_request.status_code}"
                    )
            else:
                logging.error(
                    f"Could not visit category {category_id} on page 1 - status {category_request.status_code}"
                )

    def buy(self) -> None:
        """
        Simulates to buy products in the cart with sample user data.
        :return: None
        """
        # sample user data
        user_data = {
            "firstname": "User",
            "lastname": "User",
            "adress1": "Road",
            "adress2": "City",
            "cardtype": "volvo",
            "cardnumber": "314159265359",
            "expirydate": "12/2050",
            "confirm": "Confirm",
        }
        buy_request = self.client.post(path + "/cartAction", params=user_data)
        if isinstance(buy_request, FastResponse) and buy_request.ok:
            logging.info(f"Bought products.")
        else:
            logging.error("Could not buy products.")

    def visit_profile(self) -> None:
        """
        Visits user profile.
        :return: None
        """
        profile_request = self.client.get(path + "/profile")
        if isinstance(profile_request, FastResponse) and profile_request.ok:
            logging.info("Visited profile page.")
        else:
            logging.error("Could not visit profile page.")

    def logout(self) -> None:
        """
        User logout.
        :return: None
        """
        logging.info("Completed user.")
        logout_request = self.client.post(path + "/loginAction", params={"logout": ""})
        if isinstance(logout_request, FastResponse) and logout_request.ok:
            logging.info("Successful logout.")
        else:
            logging.error(f"Could not log out - status: {logout_request.status_code}")
